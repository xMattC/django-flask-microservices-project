from django.urls import path

from app.views.dashboard_view import dashboard_view
from app.views.home_view import home_view
from app.views.projects_view import projects_view
from app.views.sessions_view import sessions_view
from app.views.task_edit_view import edit_task_view
from app.views.time_tracking_views import clock_in_view, clock_out_view

app_name = "app"

urlpatterns = [
    path("", home_view, name="home"),
    path("app/", dashboard_view, name="dashboard"),
    path("projects/", projects_view, name="projects"),
    path("sessions/", sessions_view, name="sessions"),
    path("clock-in/", clock_in_view, name="clock-in"),
    path("clock-out/", clock_out_view, name="clock-out"),
    path("tasks/<int:task_id>/edit/", edit_task_view, name="edit-task"),
]

