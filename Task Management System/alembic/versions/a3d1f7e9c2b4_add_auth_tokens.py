"""add persistent authentication tokens

Revision ID: a3d1f7e9c2b4
Revises: f087ceb12796
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3d1f7e9c2b4"
down_revision: Union[str, Sequence[str], None] = "f087ceb12796"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("token_type", sa.String(length=20), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index(op.f("ix_auth_tokens_id"), "auth_tokens", ["id"], unique=False)
    op.create_index(op.f("ix_auth_tokens_user_id"), "auth_tokens", ["user_id"], unique=False)
    op.create_index(op.f("ix_auth_tokens_token_hash"), "auth_tokens", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_auth_tokens_token_hash"), table_name="auth_tokens")
    op.drop_index(op.f("ix_auth_tokens_user_id"), table_name="auth_tokens")
    op.drop_index(op.f("ix_auth_tokens_id"), table_name="auth_tokens")
    op.drop_table("auth_tokens")