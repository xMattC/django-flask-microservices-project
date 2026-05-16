import pytest
from datetime import datetime, timedelta, timezone

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import TimeEntry


def _started():
    return datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)


def test_create_time_entry_with_required_fields():
    started_at = _started()

    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=started_at)

    assert entry.owner_user_id == "123"
    assert entry.project_id == 10
    assert entry.started_at == started_at


def test_owner_user_id_is_stored_correctly():
    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())

    assert entry.owner_user_id == "123"


def test_project_id_is_stored_correctly():
    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())

    assert entry.project_id == 10


def test_description_can_be_stored():
    entry = TimeEntry(
        owner_user_id="123", project_id=10, started_at=_started(), description="Worked on time-tracking model"
    )

    assert entry.description == "Worked on time-tracking model"


def test_description_can_be_none():
    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())

    assert entry.description is None


def test_ended_at_can_be_none_for_running_entry():
    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())

    assert entry.ended_at is None


def test_duration_seconds_returns_none_when_ended_at_is_none():
    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())

    assert entry.duration_seconds is None


def test_duration_seconds_returns_correct_seconds_when_ended_at_is_present():
    started_at = _started()
    ended_at = started_at + timedelta(hours=1, minutes=30)

    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=started_at, ended_at=ended_at)

    assert entry.duration_seconds == 5400


def test_to_dict_returns_expected_keys():
    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())
    data = entry.to_dict()

    assert set(data.keys()) == {
        "id",
        "owner_user_id",
        "project_id",
        "description",
        "started_at",
        "ended_at",
        "duration_seconds",
        "created_at",
        "updated_at",
    }


def test_to_dict_serialises_datetimes_as_iso_strings():
    started_at = _started()
    ended_at = started_at.replace(hour=10)

    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=started_at, ended_at=ended_at)
    data = entry.to_dict()

    assert data["started_at"] == started_at.isoformat()
    assert data["ended_at"] == ended_at.isoformat()


def test_to_dict_includes_duration_seconds():
    started_at = _started()
    ended_at = started_at.replace(hour=10)

    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=started_at, ended_at=ended_at)
    data = entry.to_dict()

    assert data["duration_seconds"] == 3600


def test_created_at_and_updated_at_are_set_automatically(app):
    entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())

    db.session.add(entry)
    db.session.commit()

    assert entry.created_at is not None
    assert entry.updated_at is not None


@pytest.mark.parametrize(
    "entry_data",
    [
        {"project_id": 10, "started_at": _started()},
        {"owner_user_id": "123", "started_at": _started()},
        {"owner_user_id": "123", "project_id": 10},
    ],
)
def test_required_fields_are_enforced(app, entry_data):
    entry = TimeEntry(**entry_data)

    db.session.add(entry)

    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()


def test_multiple_users_can_have_entries_without_conflict(app):
    first_entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())
    second_entry = TimeEntry(owner_user_id="456", project_id=10, started_at=_started())

    db.session.add_all([first_entry, second_entry])
    db.session.commit()

    assert first_entry.id is not None
    assert second_entry.id is not None
    assert first_entry.owner_user_id != second_entry.owner_user_id


def test_entries_can_be_queried_by_owner_user_id(app):
    first_entry = TimeEntry(owner_user_id="123", project_id=10, started_at=_started())
    second_entry = TimeEntry(owner_user_id="456", project_id=10, started_at=_started())

    db.session.add_all([first_entry, second_entry])
    db.session.commit()

    results = TimeEntry.query.filter_by(owner_user_id="123").all()

    assert len(results) == 1
    assert results[0].owner_user_id == "123"
