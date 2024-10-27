"""Removed title column form Comment table

Revision ID: db790b551de5
Revises: ffaa3b99407f
Create Date: 2024-10-27 12:49:28.888630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db790b551de5'
down_revision = 'ffaa3b99407f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('remarks')
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.drop_column('title')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('comments', schema=None) as batch_op:
        batch_op.add_column(sa.Column('title', sa.VARCHAR(length=75), nullable=False))

    op.create_table('remarks',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=75), nullable=False),
    sa.Column('content', sa.TEXT(), nullable=False),
    sa.Column('author', sa.VARCHAR(length=25), nullable=False),
    sa.Column('created_at', sa.DATETIME(), nullable=False),
    sa.Column('news_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['news_id'], ['news.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###
