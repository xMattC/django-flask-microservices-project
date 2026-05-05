class TimeEntry:

    def __init__(self, owner_user_id, project_id, started_at, description=None, ended_at=None):
        self.owner_user_id = owner_user_id
        self.project_id = project_id
        self.description = description
        self.started_at = started_at
        self.ended_at = ended_at

        self.id = None
        self.created_at = None
        self.updated_at = None

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