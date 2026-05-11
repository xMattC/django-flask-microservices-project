from django.urls import path

from app.views.dashboard_view import dashboard_view
from app.views.projects_view import projects_view
from app.views.time_tracking_views import clock_in_view, clock_out_view
from app.views.home_view import home_view

app_name = "app"

urlpatterns = [
    path("", home_view, name="home"),
    path("app/", dashboard_view, name="dashboard"),
    path("projects/", projects_view, name="projects"),
    path("clock-in/", clock_in_view, name="clock_in"),
    path("clock-out/", clock_out_view, name="clock_out"),
]
