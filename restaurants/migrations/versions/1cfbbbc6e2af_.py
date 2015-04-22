"""empty message

Revision ID: 1cfbbbc6e2af
Revises: 4dc11129504c
Create Date: 2015-04-21 14:10:20.032872

"""

# revision identifiers, used by Alembic.
revision = '1cfbbbc6e2af'
down_revision = '4dc11129504c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('attributes', sa.Column('friday', sa.Boolean(), nullable=False))
    op.add_column('attributes', sa.Column('monday', sa.Boolean(), nullable=False))
    op.add_column('attributes', sa.Column('saturday', sa.Boolean(), nullable=False))
    op.add_column('attributes', sa.Column('sunday', sa.Boolean(), nullable=False))
    op.add_column('attributes', sa.Column('thursday', sa.Boolean(), nullable=False))
    op.add_column('attributes', sa.Column('tuesday', sa.Boolean(), nullable=False))
    op.add_column('attributes', sa.Column('wednesday', sa.Boolean(), nullable=False))
    op.alter_column('city', 'name',
               existing_type=sa.VARCHAR(length=128))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('city', 'name',
               existing_type=sa.VARCHAR(length=128),
               nullable=False)
    op.drop_column('attributes', 'wednesday')
    op.drop_column('attributes', 'tuesday')
    op.drop_column('attributes', 'thursday')
    op.drop_column('attributes', 'sunday')
    op.drop_column('attributes', 'saturday')
    op.drop_column('attributes', 'monday')
    op.drop_column('attributes', 'friday')
    ### end Alembic commands ###
