"""Virustotal fix

Revision ID: b115d8e37aa2
Revises: 5b4225a35447
Create Date: 2024-05-07 04:49:52.644353

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b115d8e37aa2"
down_revision = "5b4225a35447"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("linkrequests", "virustatolid", new_column_name="virustotalid")
    op.alter_column("requests", "virustatolid", new_column_name="virustotalid")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("requests", "virustotalid", new_column_name="virustatolid")
    op.alter_column("linkrequests", "virustotalid", new_column_name="virustatolid")
    # ### end Alembic commands ###