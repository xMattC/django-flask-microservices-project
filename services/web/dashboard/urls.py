from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
]