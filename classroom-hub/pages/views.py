from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LogoutView
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect, render

from .models import Resource


def home(request):
    context = {
        "welcome_message": "Explore learning resources and project ideas.",
    }
    return render(request, "pages/home.html", context)


def resources(request):
    context = {
        "resources": Resource.objects.select_related("category").all(),
    }
    return render(request, "pages/resources.html", context)


def about(request):
    context = {
        "purpose": "Practice URL routing, views, and templates.",
    }
    return render(request, "pages/about.html", context)


class PostOnlyLogoutView(LogoutView):
    """Cierra la sesion solo con POST (y CSRF). GET responde 405."""

    http_method_names = ["post", "options"]


def signup(request):
    if request.user.is_authenticated:
        return redirect("pages:dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("pages:login")
    else:
        form = UserCreationForm()

    return render(request, "pages/signup.html", {"form": form})


@login_required
def dashboard(request):
    visit_count = request.session.get("dashboard_visits", 0) + 1
    request.session["dashboard_visits"] = visit_count

    return render(
        request,
        "pages/dashboard.html",
        {"visit_count": visit_count},
    )


@login_required
@permission_required("pages.view_resource", raise_exception=True)
def resource_review(request):
    context = {
        "resources": Resource.objects.select_related("category").all(),
    }
    return render(request, "pages/review.html", context)