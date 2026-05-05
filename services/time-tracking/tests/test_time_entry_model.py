from datetime import datetime, timezone

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
