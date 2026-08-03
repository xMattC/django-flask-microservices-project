from app.forms import ProjectCreateForm, ProjectUpdateForm
from clients import projects_service_client, time_tracking_service_client
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def _handle_create_project(request: HttpRequest):
    """Handle project creation form submission.

    Validates the submitted form and attempts to create a new project
    through the projects service.

    param request: Incoming HTTP request containing POST data.
    return:
        - Redirect response on success.
        - Error message string on failure.
        - None if form validation fails.
    """
    create_form = ProjectCreateForm(request.POST)

    if not create_form.is_valid():
        return None

    try:
        projects_service_client.create_project(request.user.id, {"name": create_form.cleaned_data["name"]})
        return redirect("app:projects")

    except projects_service_client.ProjectsServiceUnavailable:
        return "Projects service is currently unavailable."

    except projects_service_client.ProjectsServiceError:
        return "Could not create project."


def _handle_update_project(request: HttpRequest):
    """Handle project update form submission.

    Validates the submitted form and attempts to update an existing project
    through the projects service.

    param request: Incoming HTTP request containing POST data.
    return:
        - Redirect response on success.
        - Error message string on failure.
        - None if form validation fails.
    """
    update_form = ProjectUpdateForm(request.POST)

    if not update_form.is_valid():
        return None

    try:
        projects_service_client.update_project(
            update_form.cleaned_data["project_id"],
            request.user.id,  # type: ignore
            {"name": update_form.cleaned_data["name"]},
        )

        return redirect("app:projects")

    except projects_service_client.ProjectsServiceUnavailable:
        return "Projects service is currently unavailable."

    except projects_service_client.ProjectsServiceError:
        return "Could not update project."


def _handle_delete_project(request: HttpRequest):
    """Handle project deletion.

    Checks whether the project contains time tracking entries before deletion.
    Prevents deletion if related time logs exist.

    param request: Incoming HTTP request containing POST data.
    return:
        Tuple containing:
        - Redirect response or error message.
        - Project ID being deleted.
    """

    project_id = request.POST.get("project_id")

    if not project_id:
        return None, None

    project_delete_id = int(project_id)

    try:
        project_sessions = time_tracking_service_client.get_time_entries(request.user.id, project_id=project_delete_id)

        if project_sessions:
            return ("Cannot delete this project because it has time logs.", project_delete_id)

        projects_service_client.delete_project(project_delete_id, request.user.id)  # type: ignore

        if request.session.get("selected_project_id") == project_delete_id:
            request.session.pop("selected_project_id", None)

        return redirect("app:projects"), project_delete_id

    except time_tracking_service_client.TimeTrackingServiceUnavailable:
        return ("Time tracking service is currently unavailable.", project_delete_id)

    except time_tracking_service_client.TimeTrackingServiceError:
        return ("Could not check whether this project has time logs.", project_delete_id)

    except projects_service_client.ProjectsServiceUnavailable:
        return ("Projects service is currently unavailable.", project_delete_id)

    except projects_service_client.ProjectsServiceError:
        return ("Could not delete project.", project_delete_id)


def _get_projects_for_user(user_id: int):
    """Retrieve all projects for a user.

    param user_id: ID of the authenticated user.
    return:
        Tuple containing:
        - List of projects.
        - Error message or None.
    """
    try:
        return projects_service_client.get_projects(user_id), None

    except projects_service_client.ProjectsServiceUnavailable:
        return [], "Projects service is currently unavailable."

    except projects_service_client.ProjectsServiceError:
        return [], "Could not load projects."


@login_required
def projects_view(request: HttpRequest) -> HttpResponse:
    """Render and manage the projects page.

    param request: Incoming HTTP request.
    return: Rendered projects page response.
    """
    project_create_error = None
    project_update_error = None
    project_delete_error = None
    project_delete_id = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "create_project":
            result = _handle_create_project(request)

            if isinstance(result, HttpResponse):
                return result

            project_create_error = result

        elif form_type == "update_project":
            result = _handle_update_project(request)

            if isinstance(result, HttpResponse):
                return result

            project_update_error = result

        elif form_type == "delete_project":
            result, project_delete_id = _handle_delete_project(request)

            if isinstance(result, HttpResponse):
                return result

            project_delete_error = result

    projects, projects_error = _get_projects_for_user(request.user.id)  # type: ignore

    return render(
        request,
        "app/projects.html",
        {
            "projects": projects,
            "project_delete_id": project_delete_id,
            "projects_error": projects_error,
            "project_create_form": ProjectCreateForm(),
            "project_create_error": project_create_error,
            "project_update_error": project_update_error,
            "project_delete_error": project_delete_error,
        },
    )
