from collections.abc import Callable, Iterable
from typing import Any

from flask_smorest import Blueprint
from marshmallow import Schema

from app.schemas import TaskErrorSchema

USER_ID_HEADER = {
    "in": "header",
    "name": "X-User-ID",
    "schema": {"type": "string"},
    "required": True,
    "description": "User ID supplied by the Django BFF.",
}


def endpoint_docs(
    routes: Blueprint,
    *,
    success_code: int = 200,
    response_schema: type[Schema] | Schema | None = None,
    errors: Iterable[int] = (400,),
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Apply standard OpenAPI documentation to a task endpoint.

    Adds:
    - Required X-User-ID header
    - Success response and schema
    - Standard task error responses
    """

    def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        fn = routes.doc(parameters=[USER_ID_HEADER])(fn)

        if response_schema is not None:
            fn = routes.response(
                success_code,
                response_schema,
            )(fn)
        else:
            fn = routes.response(success_code)(fn)

        for status_code in reversed(tuple(errors)):
            fn = routes.alt_response(
                status_code,
                schema=TaskErrorSchema,
            )(fn)

        return fn

    return decorator
