from marshmallow import Schema, fields


class TimeEntryCreateSchema(Schema):
    """Schema for creating a new time entry."""

    project_id = fields.Integer(required=True)
    description = fields.String(allow_none=True)


class TimeEntryUpdateSchema(Schema):
    """Schema for updating an existing finished time entry."""

    project_id = fields.Integer()
    description = fields.String(allow_none=True)
    started_at = fields.DateTime(required=False)
    ended_at = fields.DateTime(required=False, allow_none=True)


class TimeEntryResponseSchema(Schema):
    """Schema representing a time entry object in API responses."""

    id = fields.Integer(required=True)
    owner_user_id = fields.String(required=True)
    project_id = fields.Integer(required=True)
    description = fields.String(allow_none=True)
    started_at = fields.DateTime(required=True)
    ended_at = fields.DateTime(allow_none=True)
    duration_seconds = fields.Integer(allow_none=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)


class TimeEntryResultsSchema(Schema):
    """Schema for wrapping time entry results in API responses."""

    results = fields.List(fields.Nested(TimeEntryResponseSchema))


class TimeEntryErrorSchema(Schema):
    """Schema representing a simple error response."""

    message = fields.String(required=True)
