import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from clients import tasks_service_client


@login_required
@require_http_methods(["PATCH"])
def edit_task_view(request, task_id):
    """Update a task title and Markdown description."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse(
            {"message": "Invalid JSON payload."},
            status=400,
        )

    task_name = data.get("task_name", "").strip()
    description = data.get("description", "")

    if not task_name:
        return JsonResponse(
            {"message": "Task title is required."},
            status=400,
        )

    try:
        task = tasks_service_client.edit_a_task(
            user_id=request.user.id,
            task_id=task_id,
            payload={
                "task_name": task_name,
                "description": description,
            },
        )
    except tasks_service_client.TasksServiceUnavailable:
        return JsonResponse(
            {"message": "Task service is unavailable."},
            status=503,
        )
    except tasks_service_client.TasksServiceError as exc:
        return JsonResponse(
            {"message": str(exc)},
            status=502,
        )

    return JsonResponse(task)
