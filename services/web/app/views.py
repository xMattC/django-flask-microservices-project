from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from clients.projects import (
    ProjectsServiceError,
    ProjectsServiceUnavailable,
    get_projects,
)


def home_view(request) -> HttpResponse:
    return render(request, "app/home.html")


@login_required
def dashboard_view(request) -> HttpResponse:
    projects = []
    projects_error = None

    try:
        projects = get_projects(request.user.id)
    except ProjectsServiceUnavailable:
        projects_error = "Projects service is currently unavailable."
    except ProjectsServiceError:
        projects_error = "Could not load projects."

    return render(
        request,
        "app/dashboard.html",
        {
            "projects": projects,
            "projects_error": projects_error,
        },
    )