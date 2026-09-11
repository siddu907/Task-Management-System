from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.task import Task
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentOut, CommentUpdate
from app.services.notification_service import create_notification, record_audit
from app.services.comment_service import add_comment as create_comment, can_modify_comment
from app.repositories.comment_repository import CommentRepository

router = APIRouter()


def task_for_user(task_id: int, user: User, db: Session) -> Task:
	from app.services.task_service import get_task as find_task
	task = find_task(db, task_id)
	if task is None: raise HTTPException(404, "Task not found")
	if user.role != "admin" and task.created_by_id != user.id and task.assigned_to_id != user.id:
		raise HTTPException(403, "Not authorized to access this task")
	return task


@router.post("/tasks/{task_id}/comments", response_model=CommentOut, status_code=201)
def add_comment(task_id: int, payload: CommentCreate, background_tasks: BackgroundTasks, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	task = task_for_user(task_id, user, db)
	try:
		comment = create_comment(db, task, user, payload.content)
	except ValueError as exc:
		raise HTTPException(400, str(exc)) from exc
	except PermissionError as exc:
		raise HTTPException(403, str(exc)) from exc
	background_tasks.add_task(record_audit, user.id, "Comment Added", "comment", comment.id)
	recipients = {task.created_by_id, task.assigned_to_id} - {user.id, None}
	for recipient in recipients:
		background_tasks.add_task(create_notification, recipient, f"A comment was added to '{task.title}'", "comment_added", task.id)
	return comment


@router.get("/tasks/{task_id}/comments", response_model=list[CommentOut])
def list_comments(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	task_for_user(task_id, user, db)
	return CommentRepository(db).list_for_task(task_id)


@router.put("/comments/{comment_id}", response_model=CommentOut)
def update_comment(comment_id: int, payload: CommentUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	comment = CommentRepository(db).get(comment_id)
	if comment is None: raise HTTPException(404, "Comment not found")
	if not can_modify_comment(comment, user): raise HTTPException(403, "Only the author or admin can modify comments")
	comment.content = payload.content; CommentRepository(db).save(); db.refresh(comment)
	return comment


@router.delete("/comments/{comment_id}")
def delete_comment(comment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	comment = CommentRepository(db).get(comment_id)
	if comment is None: raise HTTPException(404, "Comment not found")
	if not can_modify_comment(comment, user): raise HTTPException(403, "Only the author or admin can delete comments")
	repository = CommentRepository(db)
	repository.delete(comment); repository.save()
	return {"message": "Comment deleted"}
