from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '9e4606fee581'
down_revision = '4713224b8c4c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alter the 'mobile_no' column from Integer to BigInteger
    op.alter_column('users', 'mobile_no', type_=sa.BigInteger(), existing_type=sa.Integer(), nullable=False)


def downgrade() -> None:
    # Revert the 'mobile_no' column from BigInteger back to Integer
    op.alter_column('users', 'mobile_no', type_=sa.Integer(), existing_type=sa.BigInteger(), nullable=False)
