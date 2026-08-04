from datetime import datetime

from clients import projects_service_client, time_tracking_service_client
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def _format_duration(total_seconds: int | None, running: bool = False) -> str | None:
    """Format duration seconds for display."""
    if total_seconds is None:
        return None if running else "-"

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if running:
        return f"{hours}h {minutes} mins"

    return f"{hours}h {minutes}m"


def _handle_update_session(request: HttpRequest):
    """Handle session update POST request."""
    session_id_value = request.POST.get("session_id")
    started_at = request.POST.get("started_at")
    ended_at = request.POST.get("ended_at")

    if not session_id_value:
        return None

    try:
        session_id = int(session_id_value)
    except ValueError:
        return "Invalid session ID."

    try:
        time_tracking_service_client.update_time_entry(
            request.user.id,  # type: ignore[arg-type]
            session_id,
            {
                "started_at": started_at,
                "ended_at": ended_at or None,
            },
        )

        return redirect("app:sessions")

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return "Time tracking service is currently unavailable."

    except time_tracking_service_client.TimeTrackingServiceError:
        return "Could not update session."


def _handle_delete_session(request: HttpRequest):
    """Handle session delete POST request."""
    session_id_value = request.POST.get("session_id")

    if not session_id_value:
        return None

    try:
        session_id = int(session_id_value)
    except ValueError:
        return "Invalid session ID."

    try:
        time_tracking_service_client.delete_time_entry(
            request.user.id,  # type: ignore[arg-type]
            session_id,
        )

        return redirect("app:sessions")

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return "Time tracking service is currently unavailable."

    except time_tracking_service_client.TimeTrackingServiceError:
        return "Could not delete session."


def _get_sessions_for_user(user_id: int) -> tuple[list[dict], str | None]:
    """Load time-tracking sessions for a user."""
    try:
        sessions = time_tracking_service_client.get_time_entries(user_id)
        return sessions, None

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return [], "Time tracking service is currently unavailable."

    except time_tracking_service_client.TimeTrackingServiceError:
        return [], "Could not load sessions."


def _get_projects_for_user(user_id: int) -> tuple[list[dict], str | None]:
    """Load projects used to display project names."""
    try:
        projects = projects_service_client.get_projects(user_id)
        return projects, None

    except projects_service_client.ProjectsServiceUnavailable:
        return [], "Projects service is currently unavailable."

    except projects_service_client.ProjectsServiceError:
        return [], "Could not load project names."


def _build_session_display(session: dict, project_names: dict[int, str]) -> dict:
    """Build one formatted session dictionary for the UI."""
    started_at = datetime.fromisoformat(session["started_at"])

    ended_at = None
    if session["ended_at"]:
        ended_at = datetime.fromisoformat(session["ended_at"])

    project_id = session["project_id"]

    return {
        **session,
        "project_name": project_names.get(project_id, f"Project {project_id}"),
        "started_at_display": started_at.strftime("%d %b %Y %H:%M"),
        "ended_at_display": (ended_at.strftime("%d %b %Y %H:%M") if ended_at else "Running"),
        "duration_display": _format_duration(session["duration_seconds"]),
        "started_at_form": started_at.strftime("%Y-%m-%dT%H:%M"),
        "ended_at_form": (ended_at.strftime("%Y-%m-%dT%H:%M") if ended_at else ""),
    }


def _build_session_display_list(projects: list[dict], sessions: list[dict]) -> list[dict]:
    """Build formatted sessions for the sessions page."""
    project_names = {project["id"]: project["name"] for project in projects}

    return [_build_session_display(session, project_names) for session in sessions]


@login_required
def sessions_view(request: HttpRequest) -> HttpResponse:
    """Render and manage the sessions page."""
    session_update_error = None
    session_delete_error = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "update_session":
            result = _handle_update_session(request)

            if isinstance(result, HttpResponse):
                return result

            session_update_error = result

        elif form_type == "delete_session":
            result = _handle_delete_session(request)

            if isinstance(result, HttpResponse):
                return result

            session_delete_error = result

    user_id = request.user.id  # type: ignore[assignment]

    sessions, sessions_error = _get_sessions_for_user(user_id)  # type: ignore
    projects, projects_error = _get_projects_for_user(user_id)  # type: ignore

    display_sessions = _build_session_display_list(projects, sessions)

    return render(
        request,
        "app/sessions.html",
        {
            "sessions": display_sessions,
            "sessions_error": sessions_error,
            "projects_error": projects_error,
            "session_update_error": session_update_error,
            "session_delete_error": session_delete_error,
        },
    )
