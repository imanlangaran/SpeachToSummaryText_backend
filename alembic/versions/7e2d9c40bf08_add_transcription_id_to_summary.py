"""add transcription_id to summary

Revision ID: 7e2d9c40bf08
Revises: adb22c6dca50
Create Date: 2025-08-02 15:47:53.404692

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e2d9c40bf08'
down_revision: Union[str, Sequence[str], None] = 'adb22c6dca50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    with op.batch_alter_table("summaries", schema=None) as batch_op:
        batch_op.add_column(sa.Column("transcription_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_summaries_transcription_id",
            "transcriptions",
            ["transcription_id"],
            ["id"]
        )

def downgrade():
    with op.batch_alter_table("summaries", schema=None) as batch_op:
        batch_op.drop_constraint("fk_summaries_transcription_id", type_="foreignkey")
        batch_op.drop_column("transcription_id")