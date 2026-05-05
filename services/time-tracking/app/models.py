class TimeEntry:

    def __init__(self, owner_user_id, project_id, started_at, description=None, ended_at=None):
        self.owner_user_id = owner_user_id
        self.project_id = project_id
        self.started_at = started_at
        self.description = description
        self.ended_at = ended_at

    @property
    def duration_seconds(self):
        """Return duration in seconds if ended_at is set, otherwise None."""
        if self.ended_at is None:
            return None

        return int((self.ended_at - self.started_at).total_seconds())