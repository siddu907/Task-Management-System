from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.task import TaskAssignment, TaskAssignmentResponse, TaskCreate, TaskOut, TaskPriorityUpdate, TaskStatus, TaskUpdate
from app.services.notification_service import create_notification, record_audit
from app.services.task_service import change_task_status, delete_task as remove_task, get_task as find_task, list_tasks as find_tasks, save_task, validate_task_assignment

router = APIRouter()
TRANSITIONS = {"todo": {"in_progress", "cancelled"}, "in_progress": {"todo", "completed", "cancelled"}, "completed": set(), "cancelled": set()}


def can_access(task: Task, user: User) -> bool:
	return user.role == "admin" or task.created_by_id == user.id or task.assigned_to_id == user.id


def validate_assignee(db: Session, assigned_to_id: int | None):
	try:
		validate_task_assignment(db, assigned_to_id)
	except ValueError as exc:
		raise HTTPException(400, str(exc)) from exc


@router.post("", response_model=TaskOut, status_code=201)
def create_task(payload: TaskCreate, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	task = Task(**payload.model_dump(), created_by_id=user.id)
	task = save_task(db, task)
	background_tasks.add_task(record_audit, user.id, "Task Created", "task", task.id)
	return task


@router.get("", response_model=list[TaskOut])
def list_tasks(status: str | None = None, priority: str | None = None, assigned_user_id: int | None = None,
			   search: str | None = None, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100),
			   sort_by: str = Query("created_at", pattern="^(created_at|due_date|priority|status|title)$"),
			   sort_order: str = Query("desc", pattern="^(asc|desc)$"),
			   user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return find_tasks(db, user, status=status, priority=priority, assigned_user_id=assigned_user_id,
					  search=search, sort_by=sort_by, sort_order=sort_order, offset=(page - 1) * limit, limit=limit)


@router.get("/{task_id}", response_model=TaskOut)
def get_task(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	task = find_task(db, task_id)
	if task is None: raise HTTPException(404, "Task not found")
	if not can_access(task, user): raise HTTPException(403, "Not authorized to access this task")
	return task


def _update_task(task_id: int, values: dict, background_tasks: BackgroundTasks, user: User, db: Session) -> Task:
	task = get_task(task_id, user, db)
	if task.status in {"completed", "cancelled"}: raise HTTPException(400, "Closed tasks cannot be modified")
	if user.role != "admin" and task.created_by_id != user.id and set(values) - {"status", "priority"}:
		raise HTTPException(403, "Assigned users may only change status or priority")
	previous_status = task.status
	previous_assignee = task.assigned_to_id
	validate_assignee(db, values.get("assigned_to_id", task.assigned_to_id))
	if "status" in values:
		new_status = values["status"].value if isinstance(values["status"], TaskStatus) else values["status"]
		try:
			change_task_status(task, new_status)
		except ValueError as exc:
			raise HTTPException(400, str(exc)) from exc
		values["status"] = new_status
	for key, value in values.items(): setattr(task, key, value)
	task = save_task(db, task)
	background_tasks.add_task(record_audit, user.id, "Task Updated", "task", task.id)
	if previous_status != task.status:
		background_tasks.add_task(record_audit, user.id, "Task Status Changed", "task", task.id)
		recipients = {recipient for recipient in (task.assigned_to_id, task.created_by_id) if recipient and recipient != user.id}
		for recipient in recipients:
			background_tasks.add_task(create_notification, recipient, f"Task '{task.title}' status changed to {task.status}", "status_changed", task.id)
		if task.status == "completed":
			background_tasks.add_task(record_audit, user.id, "Task Completed", "task", task.id)
			for recipient in recipients:
				background_tasks.add_task(create_notification, recipient, f"Task '{task.title}' was completed", "task_completed", task.id)
	if previous_assignee != task.assigned_to_id and task.assigned_to_id:
		background_tasks.add_task(record_audit, user.id, "Task Assigned", "task", task.id)
		if previous_assignee is None:
			background_tasks.add_task(create_notification, task.assigned_to_id, f"Task '{task.title}' was assigned to you", "task_assigned", task.id)
		else:
			recipients = {previous_assignee, task.assigned_to_id, task.created_by_id} - {user.id}
			for recipient in recipients:
				message = f"Task '{task.title}' was reassigned to you" if recipient == task.assigned_to_id else f"Task '{task.title}' was reassigned"
				background_tasks.add_task(create_notification, recipient, message, "task_reassigned", task.id)
	return task


@router.put("/{task_id}", response_model=TaskOut)
def update_task(task_id: int, payload: TaskUpdate, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return _update_task(task_id, payload.model_dump(exclude_unset=True), background_tasks, user, db)


@router.delete("/{task_id}")
def delete_task(task_id: int, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	task = get_task(task_id, user, db)
	if user.role != "admin" and task.created_by_id != user.id: raise HTTPException(403, "Only the creator or admin can delete tasks")
	remove_task(db, task)
	background_tasks.add_task(record_audit, user.id, "Task Deleted", "task", task_id)
	return {"message": "Task deleted"}


@router.put("/{task_id}/assign", response_model=TaskAssignmentResponse)
def assign_task(task_id: int, payload: TaskAssignment, background_tasks: BackgroundTasks,
				user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	task = get_task(task_id, user, db)
	if user.role != "admin" and task.created_by_id != user.id:
		raise HTTPException(403, "Only the creator or admin can assign tasks")
	validate_assignee(db, payload.assigned_to_id)
	previous_assignee = task.assigned_to_id
	if previous_assignee == payload.assigned_to_id:
		return {"message": f"Task ID {task.id} is already assigned to user ID {payload.assigned_to_id}", "task": task}
	task = _update_task(task_id, {"assigned_to_id": payload.assigned_to_id}, background_tasks, user, db)
	if previous_assignee is None:
		message = f"Task ID {task.id} assigned to user ID {payload.assigned_to_id}"
	else:
		message = f"Task ID {task.id} reassigned from user ID {previous_assignee} to user ID {payload.assigned_to_id}"
	return {"message": message, "task": task}


@router.put("/{task_id}/status", response_model=TaskOut)
def change_status(task_id: int, status: TaskStatus, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return _update_task(task_id, {"status": status}, background_tasks, user, db)


@router.put("/{task_id}/priority", response_model=TaskOut)
def change_priority(task_id: int, payload: TaskPriorityUpdate, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return _update_task(task_id, {"priority": payload.priority}, background_tasks, user, db)
