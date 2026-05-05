from datetime import datetime, timezone

from app.models import TimeEntry


def test_create_time_entry_with_required_fields():
    started_at = datetime(2026, 1, 1, 9, 0, tzinfo=timezone.utc)

    entry = TimeEntry(
        owner_user_id="123",
        project_id=10,
        started_at=started_at,
    )

    assert entry.owner_user_id == "123"
    assert entry.project_id == 10
    assert entry.started_at == started_at
