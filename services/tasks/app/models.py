from datetime import datetime, timezone

from app.extensions import db


class Tasks(db.Model):
    """Database model for a single tracked time entry."""
    id = db.Column(db.Integer, primary_key=True)

    def to_dict(self):
        """Serialise the task to a dictionary."""
        return {}
