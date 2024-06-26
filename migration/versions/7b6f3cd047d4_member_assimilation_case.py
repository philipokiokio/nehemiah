"""member assimilation case

Revision ID: 7b6f3cd047d4
Revises: 5111accfab2d
Create Date: 2024-04-06 21:46:05.509200

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b6f3cd047d4"
down_revision: Union[str, None] = "5111accfab2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("members", sa.Column("address", sa.String(), nullable=True))
    op.add_column("members", sa.Column("occupation", sa.String(), nullable=True))
    op.add_column("members", sa.Column("instagram", sa.String(), nullable=True))
    op.add_column("members", sa.Column("twitter", sa.String(), nullable=True))
    op.add_column("members", sa.Column("referral", sa.String(), nullable=True))
    op.add_column("members", sa.Column("prayer_request", sa.String(), nullable=True))
    op.alter_column("members", "tribe", existing_type=sa.VARCHAR(), nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("members", "tribe", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_column("members", "prayer_request")
    op.drop_column("members", "referral")
    op.drop_column("members", "twitter")
    op.drop_column("members", "instagram")
    op.drop_column("members", "occupation")
    op.drop_column("members", "address")
    # ### end Alembic commands ###
