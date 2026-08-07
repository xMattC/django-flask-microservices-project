from clients import time_tracking_service_client
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views.decorators.http import require_POST


@login_required
@require_POST
def clock_in_view(request: HttpRequest) -> HttpResponse:
    """Start a timer for the project owned by the Active Session card."""
    project_id_value = request.POST.get("project_id")

    try:
        project_id = int(project_id_value) if project_id_value else None
    except ValueError:
        project_id = None

    if project_id is None:
        return redirect("app:dashboard")

    try:
        time_tracking_service_client.create_time_entry(
            request.user.id,
            {"project_id": project_id},
        )
    except time_tracking_service_client.TimeTrackingServiceError:
        pass

    return redirect("app:dashboard")


@login_required
@require_POST
def clock_out_view(request: HttpRequest) -> HttpResponse:
    """Stop the user's running timer, regardless of Projects-card selection."""
    try:
        running_entries = time_tracking_service_client.get_time_entries(
            request.user.id,
            running_only=True,
        )

        if running_entries:
            time_tracking_service_client.stop_time_entry(
                request.user.id,
                running_entries[0]["id"],
            )
    except time_tracking_service_client.TimeTrackingServiceError:
        pass

    return redirect("app:dashboard")
