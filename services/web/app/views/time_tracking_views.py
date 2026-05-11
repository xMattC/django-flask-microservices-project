from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect

from clients.time_tracking_service import (
    TimeTrackingServiceError,
    create_time_entry,
    get_time_entries,
    stop_time_entry,
)


@login_required
def clock_in_view(request) -> HttpResponse:
    selected_project_id = request.session.get("selected_project_id")

    if not selected_project_id:
        return redirect("app:dashboard")

    try:
        create_time_entry(request.user.id, {"project_id": selected_project_id})
    except TimeTrackingServiceError:
        pass

    return redirect("app:dashboard")


@login_required
def clock_out_view(request):
    selected_project_id = request.session.get("selected_project_id")

    running_entries = get_time_entries(
        request.user.id,
        project_id=selected_project_id,
        running_only=True,
    )

    if running_entries:
        stop_time_entry(request.user.id, running_entries[0]["id"])

    return redirect("app:dashboard")
