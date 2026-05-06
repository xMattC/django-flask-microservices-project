from flask_smorest import Blueprint

USER_ID_HEADER = {
    "in": "header",
    "name": "X-User-ID",
    "schema": {"type": "string"},
    "required": True,
    "description": "User ID supplied by the Django BFF.",
}


def endpoint_docs(routes: Blueprint, *, success_code=200):
    """Apply standardised OpenAPI documentation to a route function.

    This decorator consolidates common documentation concerns including:
    - Required X-User-ID header
    - Success response status code

    It wraps common flask-smorest documentation decorators into a single
    reusable helper to keep route definitions concise and consistent.

    Example:
        @routes.get("/projects")
        @endpoint_docs(routes)
        def get_projects():
            ...

    param routes: The Flask-Smorest Blueprint used to register documentation.
    param success_code: HTTP status code for the successful response (default: 200).

    return: A decorator that applies the configured documentation to the route function.
    """

    def decorator(fn):
        fn = routes.doc(parameters=[USER_ID_HEADER])(fn)
        fn = routes.response(success_code)(fn)

        return fn

    return decorator
