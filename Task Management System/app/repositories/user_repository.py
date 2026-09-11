from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
	def __init__(self, db: Session):
		self.db = db

	def get(self, user_id: int) -> User | None:
		return self.db.get(User, user_id)

	def get_by_email(self, email: str) -> User | None:
		normalized_email = email.strip().lower()
		return self.db.scalar(select(User).where(func.lower(User.email) == normalized_email))

	def list(self, *, active_only: bool = False) -> list[User]:
		query = select(User).order_by(User.id)
		if active_only:
			query = query.where(User.is_active.is_(True))
		return list(self.db.scalars(query).all())

	def add(self, user: User) -> User:
		self.db.add(user)
		self.db.flush()
		return user

	def save(self) -> None:
		self.db.commit()
