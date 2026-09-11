from app.models.user import User
from app.models.task import Task
from app.models.comment import Comment
from app.models.attachment import Attachment
from app.models.notification import Notification
from app.models.audit_log import AuditLog

MODEL_REGISTRY = (User, Task, Comment, Attachment, Notification, AuditLog)