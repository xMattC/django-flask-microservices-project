from datetime import datetime, timezone

from app.extensions import db


from datetime import datetime, timezone
from app.extensions import db


class Tasks(db.Model):
    """Database model for a task."""

    id = db.Column(db.Integer, primary_key=True)

    owner_user_id = db.Column(db.String(64), nullable=False, index=True)
    project_id = db.Column(db.Integer, nullable=False, index=True)

    task_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)

    state = db.Column(
        db.Enum("to-do", "in-progress", "done", name="task_state_enum"),
        nullable=False,
        default="to-do",
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        """Serialise the time entry to a dictionary."""
        return {
            "id": self.id,
            "owner_user_id": self.owner_user_id,
            "project_id": self.project_id,
            "task_name": self.task_name,
            "description": self.description,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
