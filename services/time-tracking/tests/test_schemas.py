import pytest
from datetime import datetime, timezone

from marshmallow import ValidationError

from app.schemas import (
    ErrorSchema,
    TimeEntryCreateSchema,
    TimeEntryResponseSchema,
    TimeEntryResultsSchema,
    TimeEntryUpdateSchema,
)


def test_time_entry_create_schema_accepts_valid_data():
    schema = TimeEntryCreateSchema()

    data = schema.load(
        {
            "project_id": 1,
            "description": "Worked on project setup.",
        }
    )

    assert data["project_id"] == 1
    assert data["description"] == "Worked on project setup."


def test_time_entry_create_schema_requires_project_id():
    schema = TimeEntryCreateSchema()

    with pytest.raises(ValidationError) as error:
        schema.load({"description": "Missing project ID."})

    assert "project_id" in error.value.messages


def test_time_entry_create_schema_rejects_invalid_project_id_type():
    schema = TimeEntryCreateSchema()

    with pytest.raises(ValidationError) as error:
        schema.load({"project_id": "abc", "description": "Invalid project ID."})

    assert "project_id" in error.value.messages


def test_time_entry_create_schema_allows_null_description():
    schema = TimeEntryCreateSchema()

    data = schema.load(
        {
            "project_id": 1,
            "description": None,
        }
    )

    assert data["description"] is None


def test_time_entry_update_schema_accepts_partial_data():
    schema = TimeEntryUpdateSchema()

    data = schema.load({"description": "Updated description."})

    assert data["description"] == "Updated description."


def test_time_entry_update_schema_accepts_empty_payload():
    schema = TimeEntryUpdateSchema()

    data = schema.load({})

    assert data == {}


def test_time_entry_update_schema_rejects_invalid_project_id_type():
    schema = TimeEntryUpdateSchema()

    with pytest.raises(ValidationError) as error:
        schema.load({"project_id": "abc"})

    assert "project_id" in error.value.messages


def test_time_entry_response_schema_dumps_time_entry_data():
    schema = TimeEntryResponseSchema()

    started_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    ended_at = datetime(2026, 5, 6, 11, 0, tzinfo=timezone.utc)
    created_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    updated_at = datetime(2026, 5, 6, 11, 0, tzinfo=timezone.utc)

    data = schema.dump(
        {
            "id": 1,
            "owner_user_id": "user-123",
            "project_id": 10,
            "description": "Worked on API docs.",
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_seconds": 3600,
            "created_at": created_at,
            "updated_at": updated_at,
        }
    )

    assert data["id"] == 1
    assert data["owner_user_id"] == "user-123"
    assert data["project_id"] == 10
    assert data["duration_seconds"] == 3600
    assert data["started_at"] == "2026-05-06T10:00:00+00:00"
    assert data["ended_at"] == "2026-05-06T11:00:00+00:00"


def test_time_entry_results_schema_dumps_results_list():
    schema = TimeEntryResultsSchema()

    started_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    created_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)
    updated_at = datetime(2026, 5, 6, 10, 0, tzinfo=timezone.utc)

    data = schema.dump(
        {
            "results": [
                {
                    "id": 1,
                    "owner_user_id": "user-123",
                    "project_id": 10,
                    "description": "Worked on API docs.",
                    "started_at": started_at,
                    "ended_at": None,
                    "duration_seconds": None,
                    "created_at": created_at,
                    "updated_at": updated_at,
                }
            ]
        }
    )

    assert len(data["results"]) == 1
    assert data["results"][0]["id"] == 1
    assert data["results"][0]["started_at"] == "2026-05-06T10:00:00+00:00"

def test_error_schema_dumps_message():
    schema = ErrorSchema()

    data = schema.dump({"message": "Time entry not found"})

    assert data == {"message": "Time entry not found"}
