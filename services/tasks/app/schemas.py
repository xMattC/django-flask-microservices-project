from marshmallow import Schema, fields, validate


TASK_STATES = (
    "to-do",
    "in-progress",
    "done",
)


class TaskCreateSchema(Schema):
    """Schema for creating a task."""

    project_id = fields.Integer(required=True)
    task_name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=255),
    )
    description = fields.String(
        allow_none=True,
        load_default=None,
    )
    state = fields.String(
        load_default="to-do",
        validate=validate.OneOf(TASK_STATES),
    )


class TaskUpdateSchema(Schema):
    """Schema for updating an existing task."""

    project_id = fields.Integer(required=False)
    task_name = fields.String(
        required=False,
        validate=validate.Length(min=1, max=255),
    )
    description = fields.String(
        required=False,
        allow_none=True,
    )
    state = fields.String(
        required=False,
        validate=validate.OneOf(TASK_STATES),
    )


class TaskResponseSchema(Schema):
    """Schema representing a task object in API responses."""

    id = fields.Integer(required=True)
    owner_user_id = fields.String(required=True)
    project_id = fields.Integer(required=True)
    task_name = fields.String(required=True)
    description = fields.String(allow_none=True)
    state = fields.String(required=True)
    created_at = fields.DateTime(required=True)
    updated_at = fields.DateTime(required=True)


class TaskResultsSchema(Schema):
    """Schema for wrapping task results in API responses."""

    results = fields.List(
        fields.Nested(TaskResponseSchema),
        required=True,
    )


class TaskErrorSchema(Schema):
    """Schema representing a simple error response."""

    message = fields.String(required=True)
