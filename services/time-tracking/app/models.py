class TimeEntry:

    def __init__(self, owner_user_id, project_id, started_at, description=None, ended_at=None):
        self.owner_user_id = owner_user_id
        self.project_id = project_id
        self.started_at = started_at
        self.description = description
        self.ended_at = ended_at
