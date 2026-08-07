"""add owner user id to tasks

Revision ID: 93751d4df9ea
Revises: 926824852fbb
Create Date: 2026-08-05 16:50:50.023938

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '93751d4df9ea'
down_revision = '926824852fbb'
branch_labels = None
depends_on = None


def upgrade():
    task_state_enum = sa.Enum(
        "to-do",
        "in-progress",
        "done",
        name="task_state_enum",
    )

    task_state_enum.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("owner_user_id", sa.String(length=64), nullable=False)
        )
        batch_op.add_column(
            sa.Column("project_id", sa.Integer(), nullable=False)
        )
        batch_op.add_column(
            sa.Column("task_name", sa.String(length=255), nullable=False)
        )
        batch_op.add_column(
            sa.Column("description", sa.Text(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("state", task_state_enum, nullable=False)
        )
        batch_op.add_column(
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)
        )
        batch_op.add_column(
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False)
        )

        batch_op.create_index(
            batch_op.f("ix_tasks_owner_user_id"),
            ["owner_user_id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_tasks_project_id"),
            ["project_id"],
            unique=False,
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_tasks_project_id"))
        batch_op.drop_index(batch_op.f("ix_tasks_owner_user_id"))
        batch_op.drop_column("updated_at")
        batch_op.drop_column("created_at")
        batch_op.drop_column("state")
        batch_op.drop_column("description")
        batch_op.drop_column("task_name")
        batch_op.drop_column("project_id")
        batch_op.drop_column("owner_user_id")

    task_state_enum = sa.Enum(
        "to-do",
        "in-progress",
        "done",
        name="task_state_enum",
    )

    task_state_enum.drop(op.get_bind(), checkfirst=True)
