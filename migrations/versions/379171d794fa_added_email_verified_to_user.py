"""Added email_verified to User

Revision ID: 379171d794fa
Revises: 
Create Date: 2024-09-12 20:06:12.960686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '379171d794fa'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('auth', schema=None) as batch_op:
        batch_op.add_column(sa.Column('email_verified', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('auth', schema=None) as batch_op:
        batch_op.drop_column('email_verified')

    # ### end Alembic commands ###
