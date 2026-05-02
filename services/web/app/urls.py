from django.urls import path

from app import views

app_name = "app"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("app/", views.dashboard_view, name="dashboard"),
]