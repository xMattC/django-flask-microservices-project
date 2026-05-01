from datetime import datetime, timezone

from app.extensions import db


class Project(db.Model):
    """Database model representing a project.
    This maps to the "projects" table and stores all project-related data. Each project belongs to a user,
    identified via `owner_user_id`, which comes from the Django BFF through the X-User-ID header.
        - Ownership is enforced via a simple user ID string
        - All timestamps are stored in UTC
    """

    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    owner_user_id = db.Column(db.String(255), nullable=False, index=True)

    name = db.Column(db.String(255), nullable=False)

    description = db.Column(db.Text, nullable=True)

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

    def __repr__(self):
        """Return a readable string representation of the Project.
        Useful for debugging, logging, and inspecting objects in the console.
        """
        return f"<Project id={self.id} name={self.name}>"
