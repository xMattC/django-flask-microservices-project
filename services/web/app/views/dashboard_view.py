from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from clients.projects_service import ProjectsServiceError, ProjectsServiceUnavailable, get_projects
from clients.time_tracking_service import (
    TimeTrackingServiceError,
    TimeTrackingServiceUnavailable,
    delete_time_entry,
    get_time_entries,
    update_time_entry,
)

def _handle_select_project(request: HttpRequest) -> HttpResponse:
    """Handle selected project session state."""
    project_id = request.POST.get("project_id")

    if project_id:
        request.session["selected_project_id"] = int(project_id)
    else:
        request.session.pop("selected_project_id", None)

    return redirect("app:dashboard")


def _handle_update_session(request: HttpRequest):
    """Handle session update POST request."""
    session_id = request.POST.get("session_id")
    started_at = request.POST.get("started_at")
    ended_at = request.POST.get("ended_at")

    try:
        update_time_entry(
            request.user.id,
            int(session_id),
            {
                "started_at": started_at,
                "ended_at": ended_at or None,
            },
        )

        return redirect("app:dashboard")

    except TimeTrackingServiceUnavailable:
        return "Time tracking service is currently unavailable."

    except TimeTrackingServiceError:
        return "Could not update session."


def _handle_delete_session(request: HttpRequest):
    """Handle session delete POST request."""
    session_id = request.POST.get("session_id")

    try:
        delete_time_entry(request.user.id, int(session_id))

        return redirect("app:dashboard")

    except TimeTrackingServiceUnavailable:
        return "Time tracking service is currently unavailable."

    except TimeTrackingServiceError:
        return "Could not delete session."


def _get_projects_for_user(user_id: int):
    """Load projects for a user."""
    try:
        return get_projects(user_id), None

    except ProjectsServiceUnavailable:
        return [], "Projects service is currently unavailable."

    except ProjectsServiceError:
        return [], "Could not load projects."


def _get_sessions_for_user(user_id: int):
    """Load time tracking sessions for a user."""
    try:
        return get_time_entries(user_id), None

    except TimeTrackingServiceUnavailable:
        return [], "Time tracking service is currently unavailable."

    except TimeTrackingServiceError:
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


def _build_dashboard_session(session: dict, project_names: dict[int, str]) -> dict:
    """Build one dashboard session display dictionary."""
    created_at = datetime.fromisoformat(session["created_at"])

    ended_at = None
    if session["ended_at"]:
        ended_at = datetime.fromisoformat(session["ended_at"])

    return {
        **session,
        "project_name": project_names.get(session["project_id"], f"Project {session['project_id']}"),
        "created_at_display": created_at.strftime("%d %b %Y %H:%M"),
        "ended_at_display": ended_at.strftime("%d %b %Y %H:%M") if ended_at else "Running",
        "duration_display": _format_duration(session["duration_seconds"]),
        "started_at_form": created_at.strftime("%Y-%m-%dT%H:%M"),
        "ended_at_form": ended_at.strftime("%Y-%m-%dT%H:%M") if ended_at else "",
    }


def _build_dashboard_sessions(projects: list[dict], sessions: list[dict]) -> list[dict]:
    """Build formatted dashboard sessions."""
    project_names = {project["id"]: project["name"] for project in projects}

    return [_build_dashboard_session(session, project_names) for session in sessions]


def _get_selected_project(projects: list[dict], selected_project_id: int | None) -> dict | None:
    """Return selected project from the loaded projects list."""
    if not selected_project_id:
        return None

    return next((project for project in projects if project["id"] == selected_project_id), None)


def _get_running_duration_display(dashboard_sessions: list[dict]) -> str | None:
    """Return formatted running duration if a running session exists."""
    running_session = next((session for session in dashboard_sessions if session["ended_at"] is None), None)

    if not running_session:
        return None

    return _format_duration(running_session["duration_seconds"], running=True)


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render and manage the dashboard page."""
    session_update_error = None
    session_delete_error = None
    selected_project_id = request.session.get("selected_project_id")

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "select_project":
            return _handle_select_project(request)

        if form_type == "update_session":
            result = _handle_update_session(request)

            if isinstance(result, HttpResponse):
                return result

            session_update_error = result

        if form_type == "delete_session":
            result = _handle_delete_session(request)

            if isinstance(result, HttpResponse):
                return result

            session_delete_error = result

    projects, projects_error = _get_projects_for_user(request.user.id)
    sessions, sessions_error = _get_sessions_for_user(request.user.id)

    dashboard_sessions = _build_dashboard_sessions(projects, sessions)
    has_running_session = any(session["ended_at"] is None for session in dashboard_sessions)

    return render(
        request,
        "app/dashboard.html",
        {
            "projects": projects,
            "projects_error": projects_error,
            "selected_project": _get_selected_project(projects, selected_project_id),
            "sessions": dashboard_sessions,
            "sessions_error": sessions_error,
            "session_update_error": session_update_error,
            "session_delete_error": session_delete_error,
            "has_running_session": has_running_session,
            "running_duration_display": _get_running_duration_display(dashboard_sessions),
        },
    )