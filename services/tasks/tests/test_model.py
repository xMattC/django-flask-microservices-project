from datetime import datetime

import pytest
from sqlalchemy.exc import StatementError

from app.extensions import db
from app.models import Tasks


def test_task_model_can_be_created(app):
    task = Tasks(
        owner_user_id="user-123",
        project_id=1,
        task_name="Write tests",
        description="Add model tests.",
    )

    db.session.add(task)
    db.session.commit()

    assert task.id is not None
    assert task.owner_user_id == "user-123"
    assert task.project_id == 1
    assert task.task_name == "Write tests"
    assert task.description == "Add model tests."
    assert task.state == "to-do"
    assert isinstance(task.created_at, datetime)
    assert isinstance(task.updated_at, datetime)


def test_task_model_accepts_valid_states(app):
    for state in ["to-do", "in-progress", "done"]:
        task = Tasks(
            owner_user_id=f"user-{state}",
            project_id=1,
            task_name=f"Task {state}",
            state=state,
        )

        db.session.add(task)
        db.session.commit()

        assert task.state == state


def test_task_model_rejects_invalid_state(app):
    task = Tasks(
        owner_user_id="user-123",
        project_id=1,
        task_name="Invalid state task",
        state="blocked",
    )

    db.session.add(task)

    with pytest.raises((StatementError, LookupError)):
        db.session.commit()


def test_task_to_dict_returns_expected_shape(app):
    task = Tasks(
        owner_user_id="user-123",
        project_id=7,
        task_name="Serialise task",
        description="Check dictionary output.",
        state="in-progress",
    )

    db.session.add(task)
    db.session.commit()

    result = task.to_dict()

    assert result["id"] == task.id
    assert result["owner_user_id"] == "user-123"
    assert result["project_id"] == 7
    assert result["task_name"] == "Serialise task"
    assert result["description"] == "Check dictionary output."
    assert result["state"] == "in-progress"
    assert result["created_at"] == task.created_at.isoformat()
    assert result["updated_at"] == task.updated_at.isoformat()


def test_task_description_can_be_none(app):
    task = Tasks(
        owner_user_id="user-123",
        project_id=1,
        task_name="No description task",
    )

    db.session.add(task)
    db.session.commit()

    assert task.description is None
