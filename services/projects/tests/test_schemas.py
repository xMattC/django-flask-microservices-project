import pytest
from marshmallow import ValidationError

from app.schemas import (
    ErrorSchema,
    ProjectCreateSchema,
    ProjectResponseSchema,
    ProjectResultsSchema,
    ProjectUpdateSchema,
)


def test_project_create_schema_accepts_valid_data():
    schema = ProjectCreateSchema()

    data = schema.load(
        {
            "name": "Project Alpha",
            "description": "Test project.",
        }
    )

    assert data["name"] == "Project Alpha"
    assert data["description"] == "Test project."


def test_project_create_schema_requires_name():
    schema = ProjectCreateSchema()

    with pytest.raises(ValidationError) as error:
        schema.load({"description": "Missing project name."})

    assert "name" in error.value.messages


def test_project_create_schema_rejects_empty_name():
    schema = ProjectCreateSchema()

    with pytest.raises(ValidationError) as error:
        schema.load({"name": "", "description": "Invalid project name."})

    assert "name" in error.value.messages


def test_project_create_schema_rejects_whitespace_only_name():
    schema = ProjectCreateSchema()

    with pytest.raises(ValidationError) as error:
        schema.load({"name": "   ", "description": "Invalid project name."})

    assert "name" in error.value.messages


def test_project_create_schema_allows_null_description():
    schema = ProjectCreateSchema()

    data = schema.load(
        {
            "name": "Project Alpha",
            "description": None,
        }
    )

    assert data["description"] is None


def test_project_update_schema_accepts_partial_data():
    schema = ProjectUpdateSchema()

    data = schema.load({"description": "Updated description."})

    assert data["description"] == "Updated description."


def test_project_update_schema_accepts_empty_payload():
    schema = ProjectUpdateSchema()

    data = schema.load({})

    assert data == {}


def test_project_update_schema_allows_null_description():
    schema = ProjectUpdateSchema()

    data = schema.load({"description": None})

    assert data["description"] is None


def test_project_response_schema_dumps_project_data():
    schema = ProjectResponseSchema()

    data = schema.dump(
        {
            "id": 1,
            "owner_user_id": "user-123",
            "name": "Project Alpha",
            "description": "Test project.",
        }
    )

    assert data == {
        "id": 1,
        "owner_user_id": "user-123",
        "name": "Project Alpha",
        "description": "Test project.",
    }


def test_project_results_schema_dumps_results_list():
    schema = ProjectResultsSchema()

    data = schema.dump(
        {
            "results": [
                {
                    "id": 1,
                    "owner_user_id": "user-123",
                    "name": "Project Alpha",
                    "description": None,
                }
            ]
        }
    )

    assert data == {
        "results": [
            {
                "id": 1,
                "owner_user_id": "user-123",
                "name": "Project Alpha",
                "description": None,
            }
        ]
    }


def test_error_schema_dumps_error():
    schema = ErrorSchema()

    data = schema.dump({"error": "Project not found."})

    assert data == {"error": "Project not found."}