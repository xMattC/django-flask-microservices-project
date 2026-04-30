from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render

from user.forms import RegisterForm

from django.shortcuts import render

def home_view(request):
    return render(request, "user/home.html")

def register_view(request) -> HttpResponseRedirect | HttpResponse:
    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")

    else:
        form = RegisterForm()

    return render(request, "user/register.html", {"form": form})


def login_view(request) -> HttpResponseRedirect | HttpResponse:
    error = None

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("dashboard")

        error = "Invalid email or password."

    return render(request, "user/login.html", {"error": error})


def logout_view(request) -> HttpResponseRedirect:
    logout(request)
    return redirect("login")


@login_required
def dashboard_view(request) -> HttpResponse:
    return render(request, "user/dashboard.html")