"""expand chat models

Revision ID: f00209960b4d
Revises: 6e099858b292
Create Date: 2026-11-25 15:34:40.012010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f00209960b4d'
down_revision: Union[str, Sequence[str], None] = '6e099858b292'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    if op.get_bind().dialect.name == "postgresql":
        with op.get_context().autocommit_block():
            op.execute("ALTER TYPE messagerole ADD VALUE IF NOT EXISTS 'SYSTEM'")

    op.add_column(
        "conversations",
        sa.Column("target_language", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "conversations",
        sa.Column(
            "level",
            sa.Enum("A1", "A2", "B1", "B2", "C1", "C2", name="languagelevel", create_type=False),
            nullable=True,
        ),
    )
    op.add_column(
        "conversations",
        sa.Column("topic", sa.String(length=150), nullable=True),
    )
    op.add_column(
        "conversations",
        sa.Column("is_archived", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "conversations",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index(
        op.f("ix_conversations_updated_at"),
        "conversations",
        ["updated_at"],
        unique=False,
    )

    op.add_column(
        "messages",
        sa.Column("model_name", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "messages",
        sa.Column("tokens_used", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("messages", "tokens_used")
    op.drop_column("messages", "model_name")

    op.drop_index(op.f("ix_conversations_updated_at"), table_name="conversations")
    op.drop_column("conversations", "updated_at")
    op.drop_column("conversations", "is_archived")
    op.drop_column("conversations", "topic")
    op.drop_column("conversations", "level")
    op.drop_column("conversations", "target_language")
