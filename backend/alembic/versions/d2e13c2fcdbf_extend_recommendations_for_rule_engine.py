"""extend recommendations for rule engine

Revision ID: d2e13c2fcdbf
Revises: 0c89249f9d9e
Create Date: 2026-06-22 15:33:01.487475

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd2e13c2fcdbf'
down_revision: Union[str, None] = '0c89249f9d9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE recommendations "
        "ADD COLUMN IF NOT EXISTS title VARCHAR(255)"
    )

    op.execute(
        "ALTER TABLE recommendations "
        "ADD COLUMN IF NOT EXISTS rationale TEXT"
    )

    op.execute(
        "ALTER TABLE recommendations "
        "ADD COLUMN IF NOT EXISTS priority VARCHAR(20)"
    )

    op.execute(
        "ALTER TABLE recommendations "
        "ADD COLUMN IF NOT EXISTS status VARCHAR(30)"
    )

    op.execute(
        "ALTER TABLE recommendations "
        "ADD COLUMN IF NOT EXISTS source VARCHAR(50)"
    )

    op.execute(
        "UPDATE recommendations "
        "SET title = 'Recomendación de remediación' "
        "WHERE title IS NULL"
    )

    op.execute(
        "UPDATE recommendations "
        "SET priority = 'MEDIUM' "
        "WHERE priority IS NULL"
    )

    op.execute(
        "UPDATE recommendations "
        "SET status = 'PENDING' "
        "WHERE status IS NULL"
    )

    op.execute(
        "UPDATE recommendations "
        "SET source = 'rule_engine' "
        "WHERE source IS NULL"
    )

    op.alter_column(
        "recommendations",
        "title",
        existing_type=sa.String(length=255),
        nullable=False,
    )

    op.alter_column(
        "recommendations",
        "priority",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.alter_column(
        "recommendations",
        "status",
        existing_type=sa.String(length=30),
        nullable=False,
    )

    op.alter_column(
        "recommendations",
        "source",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_recommendations_finding_source'
            ) THEN
                ALTER TABLE recommendations
                ADD CONSTRAINT uq_recommendations_finding_source
                UNIQUE (finding_id, source);
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_constraint
                WHERE conname = 'uq_recommendations_finding_source'
            ) THEN
                ALTER TABLE recommendations
                DROP CONSTRAINT uq_recommendations_finding_source;
            END IF;
        END
        $$;
        """
    )

    op.execute(
        "ALTER TABLE recommendations "
        "DROP COLUMN IF EXISTS rationale"
    )

    op.execute(
        "ALTER TABLE recommendations "
        "DROP COLUMN IF EXISTS title"
    )

    op.execute(
        "ALTER TABLE recommendations "
        "DROP COLUMN IF EXISTS priority"
    )

    op.execute(
        "ALTER TABLE recommendations "
        "DROP COLUMN IF EXISTS status"
    )

    # Ojo: si source ya existía antes de esta migración, quizás no conviene borrarla.
    # Por eso la dejamos comentada.
    # op.execute(
    #     "ALTER TABLE recommendations "
    #     "DROP COLUMN IF EXISTS source"
    # )
