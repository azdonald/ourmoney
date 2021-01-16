"""Added institiution table

Revision ID: 55a539ecc5dd
Revises: 901b1cc15eb1
Create Date: 2020-03-21 17:19:45.807542

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '55a539ecc5dd'
down_revision = '901b1cc15eb1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('institution',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('institution_id', sa.String(length=50), nullable=True),
    sa.Column('account_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['account_id'], ['account.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('institution_id'),
    sa.UniqueConstraint('name')
    )
    op.add_column('account', sa.Column('mask', sa.String(length=100), nullable=True))
    op.drop_column('account', 'official_name')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('account', sa.Column('official_name', mysql.VARCHAR(length=100), nullable=True))
    op.drop_column('account', 'mask')
    op.drop_table('institution')
    # ### end Alembic commands ###