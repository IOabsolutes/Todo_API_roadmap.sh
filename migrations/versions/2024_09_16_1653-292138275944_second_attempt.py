"""Second Attempt

Revision ID: 292138275944
Revises: 072256a65132
Create Date: 2024-09-16 16:53:09.461098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel  # added

# revision identifiers, used by Alembic.
revision: str = '292138275944'
down_revision: Union[str, None] = '072256a65132'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=True),
                    sa.Column('password_hash', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('task',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=False),
                    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
                    sa.Column('description', sa.Text(), nullable=True),
                    sa.Column('create_at', sa.DateTime(), nullable=False),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###