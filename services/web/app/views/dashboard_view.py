from datetime import datetime
from typing import Any

from clients import (
    projects_service_client,
    tasks_service_client,
    time_tracking_service_client,
)
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

ALLOWED_TASK_STATES = {
    "to-do",
    "in-progress",
    "done",
}


def _handle_select_project(request: HttpRequest) -> HttpResponse:
    """Store the project selected in the Projects card.

    This changes which project's tasks and overview are displayed. It does not
    affect the currently running time-tracking session.
    """
    project_id_value = request.POST.get("project_id")

    if not project_id_value:
        request.session.pop("selected_project_id", None)
        return redirect("app:dashboard")

    try:
        project_id = int(project_id_value)
    except (TypeError, ValueError):
        request.session.pop("selected_project_id", None)
        return redirect("app:dashboard")

    request.session["selected_project_id"] = project_id

    return redirect("app:dashboard")


def _handle_switch_project(
    request: HttpRequest,
) -> str | HttpResponse:
    """Stop the current session and start one for another project."""
    project_id_value = request.POST.get("project_id")

    if not project_id_value:
        return "Please select a project."

    try:
        project_id = int(project_id_value)
    except (TypeError, ValueError):
        return "Invalid project ID."

    user_id = request.user.id  # type: ignore

    if user_id is None:
        return "Could not identify the current user."

    try:
        running_entries = time_tracking_service_client.get_time_entries(
            user_id,
            running_only=True,
        )

        if running_entries:
            time_tracking_service_client.stop_time_entry(
                user_id,
                running_entries[0]["id"],
            )

        time_tracking_service_client.create_time_entry(
            user_id,
            {
                "project_id": project_id,
            },
        )

        # After a switch, align the Projects card with the new active project.
        # The dropdown remains independent after the user changes it again.
        request.session["selected_project_id"] = project_id

        return redirect("app:dashboard")

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return "Time tracking service is currently unavailable."

    except time_tracking_service_client.TimeTrackingServiceError:
        return "Could not switch project."


def _handle_create_task(request: HttpRequest) -> str | HttpResponse:
    """Create a task for the project selected in the Projects card."""
    project_id_value = request.POST.get("project_id")
    task_name = request.POST.get("task_name", "").strip()
    description = request.POST.get("description", "").strip()

    if not project_id_value:
        return "Please select a project before creating a task."

    try:
        project_id = int(project_id_value)
    except (TypeError, ValueError):
        return "Invalid project ID."

    if not task_name:
        return "Task name is required."

    user_id = request.user.id  # type: ignore

    if user_id is None:
        return "Could not identify the current user."

    payload = {
        "project_id": project_id,
        "task_name": task_name,
        "description": description or None,
        "state": "to-do",
    }

    try:
        tasks_service_client.create_task(
            user_id=user_id,
            payload=payload,
        )

        # Keep the task's project selected after the redirect.
        request.session["selected_project_id"] = project_id

        return redirect("app:dashboard")

    except tasks_service_client.TasksServiceUnavailable:
        return "Task service is currently unavailable."

    except tasks_service_client.TasksServiceError as exc:
        return f"Could not create task: {exc}"


def _handle_update_task_state(request: HttpRequest) -> str | HttpResponse:
    """Move a task to another workflow state."""
    task_id_value = request.POST.get("task_id")
    state = request.POST.get("state", "").strip()

    if not task_id_value:
        return "Task ID is required."

    try:
        task_id = int(task_id_value)
    except (TypeError, ValueError):
        return "Invalid task ID."

    if state not in ALLOWED_TASK_STATES:
        return "Invalid task state."

    user_id = request.user.id  # type: ignore

    if user_id is None:
        return "Could not identify the current user."

    try:
        tasks_service_client.edit_a_task(
            user_id=user_id,
            task_id=task_id,
            payload={
                "state": state,
            },
        )

        return redirect("app:dashboard")

    except tasks_service_client.TasksServiceUnavailable:
        return "Task service is currently unavailable."

    except tasks_service_client.TasksServiceError as exc:
        return f"Could not update task: {exc}"


def _handle_delete_task(request: HttpRequest) -> str | HttpResponse:
    """Delete a task belonging to the current user."""
    task_id_value = request.POST.get("task_id")

    if not task_id_value:
        return "Task ID is required."

    try:
        task_id = int(task_id_value)
    except (TypeError, ValueError):
        return "Invalid task ID."

    user_id = request.user.id  # type: ignore

    if user_id is None:
        return "Could not identify the current user."

    try:
        tasks_service_client.delete_a_task(
            user_id=user_id,
            task_id=task_id,
        )

        return redirect("app:dashboard")

    except tasks_service_client.TasksServiceUnavailable:
        return "Task service is currently unavailable."

    except tasks_service_client.TasksServiceError as exc:
        return f"Could not delete task: {exc}"


def _get_projects_for_user(user_id: int) -> tuple[list[dict[str, Any]], str | None]:
    """Load projects for a user."""
    try:
        projects = projects_service_client.get_projects(user_id)
        return projects, None

    except projects_service_client.ProjectsServiceUnavailable:
        return [], "Projects service is currently unavailable."

    except projects_service_client.ProjectsServiceError:
        return [], "Could not load projects."


def _get_sessions_for_user(user_id: int) -> tuple[list[dict[str, Any]], str | None]:
    """Load time-tracking sessions for a user."""
    try:
        sessions = time_tracking_service_client.get_time_entries(user_id)
        return sessions, None

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return [], "Time tracking service is currently unavailable."

    except time_tracking_service_client.TimeTrackingServiceError:
        return [], "Could not load sessions."


def _get_tasks_for_project(
    user_id: int, project_id: int | None
) -> tuple[list[dict[str, Any]], str | None]:
    """Load tasks for the selected project."""
    if project_id is None:
        return [], None

    try:
        tasks = tasks_service_client.get_tasks(
            user_id=user_id,
            project_id=project_id,
        )

        return tasks, None

    except tasks_service_client.TasksServiceUnavailable:
        return [], "Task service is currently unavailable."

    except tasks_service_client.TasksServiceError as exc:
        return [], f"Could not load tasks: {exc}"


def _format_duration(total_seconds: int | None, running: bool = False) -> str | None:
    """Format duration seconds for display."""
    if total_seconds is None:
        return None if running else "-"

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if running:
        return f"{hours}h {minutes} mins"

    return f"{hours}h {minutes}m"


def _parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO datetime returned by a service."""
    if not value:
        return None

    # Python's fromisoformat accepts normal offsets. Replacing Z also makes
    # explicit UTC timestamps compatible across Python versions.
    normalised_value = value.replace("Z", "+00:00")

    return datetime.fromisoformat(normalised_value)


def _build_dashboard_session(
    session: dict[str, Any], project_names: dict[int, str]
) -> dict[str, Any]:
    """Build one formatted dashboard session."""
    started_at = _parse_datetime(session.get("started_at"))
    ended_at = _parse_datetime(session.get("ended_at"))

    project_id = session.get("project_id")

    started_at_display = "-"
    if started_at is not None:
        started_at_display = started_at.strftime("%d %b %Y %H:%M")

    ended_at_display = "Running"
    if ended_at is not None:
        ended_at_display = ended_at.strftime("%d %b %Y %H:%M")

    return {
        **session,
        "project_name": project_names.get(project_id, f"Project {project_id}"),
        "started_at_display": started_at_display,
        "ended_at_display": ended_at_display,
        "duration_display": _format_duration(
            session.get("duration_seconds"),
        ),
    }


def _build_dashboard_sessions(
    projects: list[dict[str, Any]],
    sessions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Build formatted dashboard sessions."""
    project_names = {project["id"]: project["name"] for project in projects}

    return [_build_dashboard_session(session, project_names) for session in sessions]


def _get_active_session(dashboard_sessions: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the currently running session."""
    return next(
        (session for session in dashboard_sessions if session.get("ended_at") is None),
        None,
    )


def _get_last_session(dashboard_sessions: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Return the most recently started session."""
    if not dashboard_sessions:
        return None

    return dashboard_sessions[0]


def _get_project_by_id(
    projects: list[dict[str, Any]], project_id: int | None
) -> dict[str, Any] | None:
    """Return a project matching the supplied ID."""
    if project_id is None:
        return None

    return next(
        (project for project in projects if project.get("id") == project_id),
        None,
    )


def _normalise_selected_project_id(selected_project_id: object) -> int | None:
    """Convert the selected project session value into an integer."""
    if selected_project_id is None:
        return None

    try:
        return int(selected_project_id)
    except (TypeError, ValueError):
        return None


def _split_tasks_by_state(
    tasks: list[dict[str, Any]],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    """Split tasks into the three dashboard workflow columns."""
    todo_tasks = []
    in_progress_tasks = []
    done_tasks = []

    for task in tasks:
        state = task.get("state")

        if state in {"to-do", "todo"}:
            todo_tasks.append(task)
        elif state == "in-progress":
            in_progress_tasks.append(task)
        elif state == "done":
            done_tasks.append(task)

    return (
        todo_tasks,
        in_progress_tasks,
        done_tasks,
    )


@login_required
def dashboard_view(request: HttpRequest) -> HttpResponse:
    """Render and manage the dashboard."""
    switch_project_error = None
    task_create_error = None
    task_update_error = None
    task_delete_error = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "select_project":
            return _handle_select_project(request)

        if form_type == "switch_project":
            result = _handle_switch_project(request)

            if isinstance(result, HttpResponse):
                return result

            switch_project_error = result

        elif form_type == "create_task":
            result = _handle_create_task(request)

            if isinstance(result, HttpResponse):
                return result

            task_create_error = result

        elif form_type == "update_task_state":
            result = _handle_update_task_state(request)

            if isinstance(result, HttpResponse):
                return result

            task_update_error = result

        elif form_type == "delete_task":
            result = _handle_delete_task(request)

            if isinstance(result, HttpResponse):
                return result

            task_delete_error = result

    user_id = request.user.id

    if user_id is None:
        return redirect("login")

    projects, projects_error = _get_projects_for_user(user_id)
    sessions, sessions_error = _get_sessions_for_user(user_id)

    dashboard_sessions = _build_dashboard_sessions(
        projects,
        sessions,
    )

    active_session = _get_active_session(dashboard_sessions)
    last_session = _get_last_session(dashboard_sessions)
    display_session = active_session or last_session

    active_project_id = None

    if display_session is not None:
        active_project_id = display_session.get("project_id")

    active_project = _get_project_by_id(
        projects,
        active_project_id,
    )

    selected_project_id = _normalise_selected_project_id(
        request.session.get("selected_project_id"),
    )

    # On the initial dashboard load, the Projects dropdown should match the
    # project shown by the Active Session card. Once the user selects another
    # project, the dropdown is stored separately in the Django session.
    if selected_project_id is None:
        selected_project_id = active_project_id

        if selected_project_id is not None:
            request.session["selected_project_id"] = selected_project_id

    selected_project = _get_project_by_id(
        projects,
        selected_project_id,
    )

    # A stale session value may refer to a deleted or inaccessible project.
    # Fall back to the active project and repair the stored session value.
    if selected_project is None and selected_project_id is not None:
        selected_project_id = active_project_id
        selected_project = active_project

        if selected_project_id is None:
            request.session.pop("selected_project_id", None)
        else:
            request.session["selected_project_id"] = selected_project_id

    tasks, tasks_error = _get_tasks_for_project(
        user_id=user_id,
        project_id=selected_project_id,
    )

    (
        todo_tasks,
        in_progress_tasks,
        done_tasks,
    ) = _split_tasks_by_state(tasks)

    running_duration_display = None

    if active_session is not None:
        running_duration_display = _format_duration(
            active_session.get("duration_seconds"),
            running=True,
        )

    return render(
        request,
        "app/dashboard.html",
        {
            "projects": projects,
            "projects_error": projects_error,
            # Active Session card state
            "active_session": active_session,
            "active_project": active_project,
            "display_project": active_project,
            "display_session": display_session,
            "last_session": last_session,
            "active_session_error": sessions_error,
            "running_duration_display": running_duration_display,
            "switch_project_error": switch_project_error,
            # Independent Projects card state
            "selected_project": selected_project,
            "selected_project_id": selected_project_id,
            # Task card state
            "tasks": tasks,
            "tasks_error": tasks_error,
            "todo_tasks": todo_tasks,
            "in_progress_tasks": in_progress_tasks,
            "done_tasks": done_tasks,
            "task_create_error": task_create_error,
            "task_update_error": task_update_error,
            "task_delete_error": task_delete_error,
        },
    )
