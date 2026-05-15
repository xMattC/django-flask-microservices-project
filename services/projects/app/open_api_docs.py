from flask_smorest import Blueprint

from app.schemas import ProjectErrorSchema

USER_ID_HEADER = {
    "in": "header",
    "name": "X-User-ID",
    "schema": {"type": "string"},
    "required": True,
    "description": "User ID supplied by the Django BFF.",
}


def endpoint_docs(routes: Blueprint, *, success_code=200, response_schema=None, errors=(400,)):
    """Apply standardised OpenAPI documentation to a route function.

    This decorator consolidates common documentation concerns including:
    - Required X-User-ID header
    - Success response schema and status code
    - Standardised error responses

    It wraps multiple flask-smorest decorators into a single reusable helper
    to keep route definitions concise and consistent.

    Example:
        @routes.get("/projects")
        @endpoint_docs(routes, response_schema=ProjectResultsSchema)
        def get_projects():
            ...

    param routes: The Flask-Smorest Blueprint used to register documentation.
    param success_code: HTTP status code for the successful response (default: 200).
    param response_schema: Marshmallow schema for the success response. If None, no schema is applied.
    param errors: Iterable of HTTP status codes to document using the ErrorSchema.

    return: A decorator that applies the configured documentation to the route function.
    """

    def decorator(fn):
        fn = routes.doc(parameters=[USER_ID_HEADER])(fn)

        if response_schema is not None:
            fn = routes.response(success_code, response_schema)(fn)
        else:
            fn = routes.response(success_code)(fn)

        for status_code in reversed(errors):
            fn = routes.alt_response(status_code, schema=ProjectErrorSchema)(fn)

        return fn

    return decorator
