"""add recommendation text column

Revision ID: fc0ed44ea443
Revises: d2e13c2fcdbf
Create Date: 2026-06-22 15:55:35.574914

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fc0ed44ea443'
down_revision: Union[str, None] = 'd2e13c2fcdbf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute(
        "ALTER TABLE recommendations "
        "ADD COLUMN IF NOT EXISTS recommendation_text TEXT"
    )

    op.execute(
        "UPDATE recommendations "
        "SET recommendation_text = 'Recomendación pendiente de generación.' "
        "WHERE recommendation_text IS NULL"
    )

    op.alter_column(
        "recommendations",
        "recommendation_text",
        existing_type=sa.Text(),
        nullable=False,
    )

def downgrade() -> None:
    op.execute(
        "ALTER TABLE recommendations "
        "DROP COLUMN IF EXISTS recommendation_text"
    )
