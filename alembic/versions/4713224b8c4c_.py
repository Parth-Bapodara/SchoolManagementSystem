"""empty message

Revision ID: 4713224b8c4c
Revises: b3c214722ea9
Create Date: 2024-12-06 15:25:00.949737

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4713224b8c4c'
down_revision = 'b3c214722ea9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Set a default value (e.g., 0) for existing rows where mobile_no is NULL
    op.execute("UPDATE users SET mobile_no = 0 WHERE mobile_no IS NULL")
    
    # Now apply the ALTER COLUMN statement to set mobile_no as NOT NULL
    op.alter_column('users', 'mobile_no',
               existing_type=sa.INTEGER(),
               nullable=False)

def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('users', 'mobile_no',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
