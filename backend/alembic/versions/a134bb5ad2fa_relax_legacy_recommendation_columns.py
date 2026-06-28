from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a134bb5ad2fa"
down_revision: Union[str, None] = "fc0ed44ea443"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        DECLARE
            col_name text;
        BEGIN
            FOREACH col_name IN ARRAY ARRAY[
                'description',
                'review_status',
                'generated_at',
                'reviewed_at',
                'reviewed_by_user_id',
                'model_provider',
                'model_name',
                'confidence_score'
            ]
            LOOP
                IF EXISTS (
                    SELECT 1
                    FROM information_schema.columns
                    WHERE table_name = 'recommendations'
                    AND column_name = col_name
                ) THEN
                    EXECUTE format(
                        'ALTER TABLE recommendations ALTER COLUMN %I DROP NOT NULL',
                        col_name
                    );
                END IF;
            END LOOP;
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
                FROM information_schema.columns
                WHERE table_name = 'recommendations'
                AND column_name = 'description'
            ) THEN
                ALTER TABLE recommendations
                ALTER COLUMN description SET NOT NULL;
            END IF;
        END
        $$;
        """
    )
