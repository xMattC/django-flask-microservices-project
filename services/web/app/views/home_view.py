from django.http import HttpRequest, HttpResponse
from django.shortcuts import render



def home_view(request: HttpRequest) -> HttpResponse:
    """Render the application home page.

    param request: Incoming HTTP request.
    return: Rendered home page response.
    """
    return render(request, "app/home.html")