from fastapi import FastAPI
from app.routers import auth, user, tasks, comment, attachments, notifications, dashboard, audit_logs

app = FastAPI(title="Task Management System", version="1.0.0")


app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(user.router, prefix="/users", tags=["Users"])
app.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
app.include_router(comment.router, tags=["Comments"])
app.include_router(attachments.router, tags=["Attachments"])
app.include_router(notifications.router, prefix="/notifications", tags=["Notifications"])
app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
app.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])




