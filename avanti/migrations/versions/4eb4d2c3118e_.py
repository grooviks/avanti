"""empty message

Revision ID: 4eb4d2c3118e
Revises: 
Create Date: 2020-01-07 12:06:08.455300

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4eb4d2c3118e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=300), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.Column('lft', sa.Integer(), nullable=False),
    sa.Column('rgt', sa.Integer(), nullable=False),
    sa.Column('level', sa.Integer(), nullable=False),
    sa.Column('tree_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('categories_level_idx', 'categories', ['level'], unique=False)
    op.create_index('categories_lft_idx', 'categories', ['lft'], unique=False)
    op.create_index('categories_rgt_idx', 'categories', ['rgt'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=False),
    sa.Column('full_name', sa.String(length=200), nullable=True),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.Column('role', sa.Integer(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('birth_date', sa.DateTime(), nullable=True),
    sa.Column('phone', sa.String(length=20), nullable=True),
    sa.Column('reg_date', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('username')
    )
    op.create_table('category_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=80), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=300), nullable=True),
    sa.Column('price', sa.Numeric(precision=10, scale=0), nullable=True),
    sa.Column('number', sa.Integer(), nullable=True),
    sa.Column('detail', sa.Text(), nullable=True),
    sa.Column('tips', sa.Text(), nullable=True),
    sa.Column('is_avail', sa.Boolean(), nullable=True),
    sa.Column('is_hot', sa.Boolean(), nullable=True),
    sa.Column('is_new', sa.Boolean(), nullable=True),
    sa.Column('category_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('product_images',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(length=80), nullable=True),
    sa.Column('product_id', sa.Integer(), nullable=True),
    sa.Column('basic_image', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('product_images')
    op.drop_table('products')
    op.drop_table('category_images')
    op.drop_table('users')
    op.drop_index('categories_rgt_idx', table_name='categories')
    op.drop_index('categories_lft_idx', table_name='categories')
    op.drop_index('categories_level_idx', table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
