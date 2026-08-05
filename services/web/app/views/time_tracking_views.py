from clients import time_tracking_service_client
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect


@login_required
def clock_in_view(request) -> HttpResponse:
    selected_project_id = request.session.get("selected_project_id")

    if not selected_project_id:
        return redirect("app:dashboard")

    try:
        time_tracking_service_client.create_time_entry(
            request.user.id, {"project_id": selected_project_id}
        )
    except time_tracking_service_client.TimeTrackingServiceError:
        pass

    return redirect("app:dashboard")


@login_required
def clock_out_view(request):
    print("CLOCK OUT VIEW")
    selected_project_id = request.session.get("selected_project_id")
    print("Selected project:", selected_project_id)
    running_entries = time_tracking_service_client.get_time_entries(
        request.user.id,
        project_id=selected_project_id,
        running_only=True,
    )
    print(
        time_tracking_service_client.get_time_entries(
            request.user.id,
            running_only=True,
        )
    )
    print("Running entries:", running_entries)
    if running_entries:
        time_tracking_service_client.stop_time_entry(request.user.id, running_entries[0]["id"])

    return redirect("app:dashboard")
