from datetime import datetime

from clients import projects_service_client, time_tracking_service_client
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def _handle_select_project(request: HttpRequest) -> HttpResponse:
    """Handle selected project session state."""
    project_id = request.POST.get("project_id")

    if project_id:
        request.session["selected_project_id"] = int(project_id)
    else:
        request.session.pop("selected_project_id", None)

    return redirect("app:dashboard")


def _handle_switch_project(request: HttpRequest):
    """Stop the current session and start one for another project."""
    project_id_value = request.POST.get("project_id")

    if not project_id_value:
        return "Please select a project."

    try:
        project_id = int(project_id_value)
    except ValueError:
        return "Invalid project ID."

    user_id = request.user.id  # type: ignore[arg-type]

    try:
        running_entries = time_tracking_service_client.get_time_entries(
            user_id, running_only=True  # type: ignore
        )

        if running_entries:
            time_tracking_service_client.stop_time_entry(
                user_id, running_entries[0]["id"]  # type: ignore
            )

        time_tracking_service_client.create_time_entry(
            user_id, {"project_id": project_id}  # type: ignore
        )

        request.session["selected_project_id"] = project_id

        return redirect("app:dashboard")

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return "Time tracking service is currently unavailable."

    except time_tracking_service_client.TimeTrackingServiceError:
        return "Could not switch project."


def _get_projects_for_user(user_id: int) -> tuple[list[dict], str | None]:
    """Load projects for a user."""
    try:
        return projects_service_client.get_projects(user_id), None

    except projects_service_client.ProjectsServiceUnavailable:
        return [], "Projects service is currently unavailable."

    except projects_service_client.ProjectsServiceError:
        return [], "Could not load projects."


def _get_sessions_for_user(user_id: int) -> tuple[list[dict], str | None]:
    """Load time-tracking sessions for a user."""
    try:
        return time_tracking_service_client.get_time_entries(user_id), None

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return [], "Time tracking service is currently unavailable."

    except time_tracking_service_client.TimeTrackingServiceError:
        return [], "Could not load sessions."


def _format_duration(total_seconds: int | None, running: bool = False) -> str | None:
    """Format duration seconds for display."""
    if total_seconds is None:
        return None if running else "-"

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if running:
        return f"{hours}h {minutes} mins"

    return f"{hours}h {minutes}m"


def _build_dashboard_session(
    session: dict,
    project_names: dict[int, str],
) -> dict:
    """Build one formatted dashboard session."""

    # Your API response uses started_at for the actual session start.
    started_at = datetime.fromisoformat(session["started_at"])

    ended_at = None
    if session["ended_at"]:
        ended_at = datetime.fromisoformat(session["ended_at"])

    project_id = session["project_id"]

    return {
        **session,
        "project_name": project_names.get(
            project_id,
            f"Project {project_id}",
        ),
        "started_at_display": started_at.strftime("%d %b %Y %H:%M"),
        "ended_at_display": (ended_at.strftime("%d %b %Y %H:%M") if ended_at else "Running"),
        "duration_display": _format_duration(session["duration_seconds"]),
    }


def _build_dashboard_sessions(projects: list[dict], sessions: list[dict]) -> list[dict]:
    """Build formatted dashboard sessions."""
    project_names = {project["id"]: project["name"] for project in projects}

    return [_build_dashboard_session(session, project_names) for session in sessions]


def _get_active_session(dashboard_sessions: list[dict]) -> dict | None:
    """Return the currently running session."""
    return next(
        (session for session in dashboard_sessions if session["ended_at"] is None),
        None,
    )


def _get_last_session(dashboard_sessions: list[dict]) -> dict | None:
    """Return the most recently started session."""
    if not dashboard_sessions:
        return None

    return dashboard_sessions[0]


def _get_selected_project(
    projects: list[dict],
    selected_project_id: int | None,
) -> dict | None:
    """Return the selected project."""
    if not selected_project_id:
        return None

    return next(
        (project for project in projects if project["id"] == selected_project_id),
        None,
    )


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render and manage the dashboard."""
    switch_project_error = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "select_project":
            return _handle_select_project(request)

        if form_type == "switch_project":
            result = _handle_switch_project(request)

            if isinstance(result, HttpResponse):
                return result

            switch_project_error = result

    user_id = request.user.id  # type: ignore[arg-type]
    selected_project_id = request.session.get("selected_project_id")

    projects, projects_error = _get_projects_for_user(user_id)  # type: ignore
    sessions, sessions_error = _get_sessions_for_user(user_id)  # type: ignore

    dashboard_sessions = _build_dashboard_sessions(projects, sessions)

    active_session = _get_active_session(dashboard_sessions)
    last_session = _get_last_session(dashboard_sessions)

    display_session = active_session or last_session

    if selected_project_id is None and last_session:
        selected_project_id = last_session["project_id"]

    running_duration_display = None

    if active_session:
        running_duration_display = _format_duration(
            active_session["duration_seconds"],
            running=True,
        )

    return render(
        request,
        "app/dashboard.html",
        {
            "projects": projects,
            "projects_error": projects_error,
            "display_project": active_session or last_session,
            "selected_project": _get_selected_project(projects, selected_project_id),
            "active_session": active_session,
            "display_session": display_session,
            "last_session": last_session,
            "active_session_error": sessions_error,
            "running_duration_display": running_duration_display,
            "switch_project_error": switch_project_error,
        },
    )
