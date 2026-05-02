from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render


def home_view(request) -> HttpResponse:
    return render(request, "app/home.html")

@login_required
def dashboard_view(request) -> HttpResponse:
    return render(request, "app/dashboard.html")