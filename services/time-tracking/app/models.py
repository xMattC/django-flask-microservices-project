from datetime import datetime, timezone

from app.extensions import db


class TimeEntry(db.Model):
    """Database model for a single tracked time entry."""

    __tablename__ = "time_entries"

    id = db.Column(db.Integer, primary_key=True)
    owner_user_id = db.Column(db.String(64), nullable=False, index=True)
    project_id = db.Column(db.Integer, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False)
    ended_at = db.Column(db.DateTime(timezone=True), nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @property
    def duration_seconds(self):
        """Return duration in seconds if ended_at is set, otherwise None."""
        if self.ended_at is None:
            return None

        return int((self.ended_at - self.started_at).total_seconds())

    def to_dict(self):
        """Serialise the time entry to a dictionary."""
        return {
            "id": self.id,
            "owner_user_id": self.owner_user_id,
            "project_id": self.project_id,
            "description": self.description,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "duration_seconds": self.duration_seconds,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
