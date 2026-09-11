from app.database import SessionLocal
from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository
from app.repositories.user_repository import UserRepository


def test_audit_repository_crud():
    with SessionLocal() as db:
        repository = AuditRepository(db)
        log = repository.add(AuditLog(user_id=None, action="Test", entity_type="test"))
        repository.save()
        assert repository.get(log.id) is not None
        assert repository.list(limit=10)


def test_user_repository_lookup():
    with SessionLocal() as db:
        repository = UserRepository(db)
        users = repository.list()
        if users:
            assert repository.get(users[0].id) is not None
            assert repository.get_by_email(users[0].email) is not None
