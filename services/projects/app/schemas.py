from marshmallow import Schema, fields, validates, ValidationError


class ProjectCreateSchema(Schema):
    """Schema for creating a new project.

    This schema validates incoming request data when creating a project.
    It ensures that required fields are present and conform to expected formats.

    Fields:
    - name: Project name. Must be a non-empty string.
    - description: Optional project description. Can be null.

    Validation:
    - name must not be empty or whitespace-only.
    """

    name = fields.String(required=True)
    description = fields.String(allow_none=True)

    @validates("name")
    def validate_name(self, value, **kwargs):
        """Validate the project name field.

        param value: The provided project name.
        return: None.
        raises ValidationError: If the name is empty or whitespace-only.
        """
        if not value.strip():
            raise ValidationError("Project name is required.")


class ProjectUpdateSchema(Schema):
    """Schema for updating an existing project.

    This schema is used for partial updates (PATCH requests). All fields are optional,
    but any provided values must conform to expected formats.

    Fields:
    - name: Optional updated project name.
    - description: Optional updated project description. Can be null.
    """

    name = fields.String()
    description = fields.String(allow_none=True)


class ProjectResponseSchema(Schema):
    """Schema representing a project object in responses.

    This schema defines the structure of a project as returned by the API.

    Fields:
    - id: Unique project identifier.
    - owner_user_id: Identifier of the user who owns the project.
    - name: Project name.
    - description: Optional project description.
    """

    id = fields.Integer(required=True)
    owner_user_id = fields.String(required=True)
    name = fields.String(required=True)
    description = fields.String(allow_none=True)


class ProjectResultsSchema(Schema):
    """Schema for wrapping project results in API responses.

    This schema standardises responses that return one or more projects
    by enclosing them in a "results" list.

    Fields:
    - results: List of project objects.
    """

    results = fields.List(fields.Nested(ProjectResponseSchema))


class ProjectErrorSchema(Schema):
    """Schema representing a simple error response.

    This schema defines the structure for custom error responses returned
    by the API.

    Fields:
    - error: Error message describing what went wrong.
    """

    error = fields.String(required=True)
