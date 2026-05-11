from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from clients.projects_service import (
    ProjectsServiceError,
    ProjectsServiceUnavailable,
    get_projects,
)
from clients.time_tracking_service import (
    TimeTrackingServiceError,
    TimeTrackingServiceUnavailable,
    get_time_entries,
    update_time_entry,
    delete_time_entry,
)


def home_view(request) -> HttpResponse:
    return render(request, "app/home.html")


@login_required
def dashboard_view(request) -> HttpResponse:
    projects = []
    projects_error = None
    sessions = []
    sessions_error = None
    session_update_error = None
    session_delete_error = None

    selected_project_id = request.session.get("selected_project_id")

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "select_project":
            project_id = request.POST.get("project_id")

            if project_id:
                request.session["selected_project_id"] = int(project_id)
            else:
                request.session.pop("selected_project_id", None)

            return redirect("app:dashboard")

        if form_type == "update_session":
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
                session_update_error = "Time tracking service is currently unavailable."

            except TimeTrackingServiceError:
                session_update_error = "Could not update session."

        if form_type == "delete_session":
            session_id = request.POST.get("session_id")

            try:
                delete_time_entry(request.user.id, int(session_id))

                return redirect("app:dashboard")

            except TimeTrackingServiceUnavailable:
                session_delete_error = "Time tracking service is currently unavailable."

            except TimeTrackingServiceError:
                session_delete_error = "Could not delete session."

    try:
        projects = get_projects(request.user.id)
    except ProjectsServiceUnavailable:
        projects_error = "Projects service is currently unavailable."
    except ProjectsServiceError:
        projects_error = "Could not load projects."

    try:
        sessions = get_time_entries(request.user.id)
    except TimeTrackingServiceUnavailable:
        sessions_error = "Time tracking service is currently unavailable."
    except TimeTrackingServiceError:
        sessions_error = "Could not load sessions."

    project_names = {project["id"]: project["name"] for project in projects}

    dashboard_sessions = []

    for session in sessions:
        created_at = datetime.fromisoformat(session["created_at"])

        ended_at = None
        if session["ended_at"]:
            ended_at = datetime.fromisoformat(session["ended_at"])

        duration_display = "-"

        if session["duration_seconds"] is not None:
            total_seconds = session["duration_seconds"]

            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60

            duration_display = f"{hours}h {minutes}m"

        dashboard_sessions.append(
            {
                **session,
                "project_name": project_names.get(
                    session["project_id"],
                    f"Project {session['project_id']}",
                ),
                "created_at_display": created_at.strftime("%d %b %Y %H:%M"),
                "ended_at_display": (ended_at.strftime("%d %b %Y %H:%M") if ended_at else "Running"),
                "duration_display": duration_display,
                "started_at_form": created_at.strftime("%Y-%m-%dT%H:%M"),
                "ended_at_form": (ended_at.strftime("%Y-%m-%dT%H:%M") if ended_at else ""),
            }
        )

    has_running_session = any(session["ended_at"] is None for session in dashboard_sessions)

    running_duration_display = None

    running_session = next(
        (session for session in dashboard_sessions if session["ended_at"] is None),
        None,
    )

    if running_session and running_session["duration_seconds"] is not None:
        total_seconds = running_session["duration_seconds"]

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60

        running_duration_display = f"{hours}h {minutes} mins"

    selected_project = None
    if selected_project_id:
        selected_project = next(
            (project for project in projects if project["id"] == selected_project_id),
            None,
        )

    return render(
        request,
        "app/dashboard.html",
        {
            "projects": projects,
            "projects_error": projects_error,
            "selected_project": selected_project,
            "sessions": dashboard_sessions,
            "sessions_error": sessions_error,
            "session_update_error": session_update_error,
            "session_delete_error": session_delete_error,
            "has_running_session": has_running_session,
            "running_duration_display": running_duration_display,
        },
    )
