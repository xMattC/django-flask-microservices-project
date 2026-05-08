from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render

from clients.projects_service import (
    ProjectsServiceError,
    ProjectsServiceUnavailable,
    create_project,
    delete_project,
    get_projects,
    update_project,
)
from clients.time_tracking_service import (
    TimeTrackingServiceError,
    TimeTrackingServiceUnavailable,
    create_time_entry,
    get_time_entries,
    stop_time_entry,
)

from .forms import ProjectCreateForm, ProjectUpdateForm


def home_view(request) -> HttpResponse:
    return render(request, "app/home.html")


@login_required
def dashboard_view(request) -> HttpResponse:
    projects = []
    projects_error = None
    sessions = []
    sessions_error = None

    selected_project_id = request.session.get("selected_project_id")

    if request.method == "POST" and request.POST.get("form_type") == "select_project":
        project_id = request.POST.get("project_id")

        if project_id:
            request.session["selected_project_id"] = int(project_id)
        else:
            request.session.pop("selected_project_id", None)

        return redirect("app:dashboard")

    try:
        projects = get_projects(request.user.id)
    except ProjectsServiceUnavailable:
        projects_error = "Projects service is currently unavailable."
    except ProjectsServiceError:
        projects_error = "Could not load projects."

    try:
        sessions = get_time_entries(request.user.id)
    except Exception as exc:
        sessions_error = str(exc)

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
            "sessions": sessions,
            "sessions_error": sessions_error,
        },
    )


@login_required
def projects_view(request) -> HttpResponse:
    projects = []
    projects_error = None
    project_create_error = None
    project_update_error = None
    project_delete_error = None

    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "create_project":
            create_form = ProjectCreateForm(request.POST)

            if create_form.is_valid():
                try:
                    create_project(
                        request.user.id,
                        {"name": create_form.cleaned_data["name"]},
                    )
                    return redirect("app:projects")

                except ProjectsServiceUnavailable:
                    project_create_error = "Projects service is currently unavailable."

                except ProjectsServiceError:
                    project_create_error = "Could not create project."

        elif form_type == "update_project":
            update_form = ProjectUpdateForm(request.POST)

            if update_form.is_valid():
                try:
                    update_project(
                        update_form.cleaned_data["project_id"],
                        request.user.id,
                        {"name": update_form.cleaned_data["name"]},
                    )
                    return redirect("app:projects")

                except ProjectsServiceUnavailable:
                    project_update_error = "Projects service is currently unavailable."

                except ProjectsServiceError:
                    project_update_error = "Could not update project."

        elif form_type == "delete_project":
            project_id = request.POST.get("project_id")

            if project_id:
                try:
                    delete_project(int(project_id), request.user.id)

                    if request.session.get("selected_project_id") == int(project_id):
                        request.session.pop("selected_project_id", None)

                    return redirect("app:projects")

                except ProjectsServiceUnavailable:
                    project_delete_error = "Projects service is currently unavailable."

                except ProjectsServiceError:
                    project_delete_error = "Could not delete project."

    try:
        projects = get_projects(request.user.id)
    except ProjectsServiceUnavailable:
        projects_error = "Projects service is currently unavailable."
    except ProjectsServiceError:
        projects_error = "Could not load projects."

    return render(
        request,
        "app/projects.html",
        {
            "projects": projects,
            "projects_error": projects_error,
            "project_create_form": ProjectCreateForm(),
            "project_create_error": project_create_error,
            "project_update_error": project_update_error,
            "project_delete_error": project_delete_error,
        },
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
