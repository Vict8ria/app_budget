from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from datetime import date

from . import forms
from . import models


# Create your views here.
def landing(request):
    return render(request, "landing/index.html")


# def dashboard(request):
#     return render(request, "app/dashboard.html")


def user_login(request):
    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                username=cd['username'],
                password=cd['password'],
            )

            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('User was logged in')
                else:
                    return HttpResponse('User not active')
            else:
                return HttpResponse('Bad credentials')
    else:
        form = forms.LoginForm()
        return render(request, 'registration/login.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'app/profile.html', {'user': request.user})


def register(request):
    if request.method == "POST":
        form = forms.RegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_user = form.save(commit=False)
            new_user.set_password(
                cd['password'],
            )
            new_user.save()
            models.Profile.objects.create(user=new_user)
            return render(request, 'registration/registration_complete.html', {'new_user': new_user})
    else:
        form = forms.RegistrationForm()
        return render(request, 'registration/registration.html', {'form': form})


@login_required
def all_projects(request):
    today = date.today()
    projects = models.Project.objects.all()
    return render(request, "app/projects_list.html", {"projects": projects, "today": today})


@login_required
def detailed_project(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    return render(request, "app/project.html", {"project": project})


@login_required
def create_project(request):
    if request.method == "POST":
        project_form = forms.CreateProjectForm(request.POST)
        if project_form.is_valid():
            new_project = project_form.save(commit=False)
            new_project.user = request.user
            new_project.save()
            return redirect(reverse("detailed_project", args=[new_project.id]))
    else:
        project_form = forms.CreateProjectForm()
        return render(request, 'app/create_project.html', {'form': project_form})


@login_required
def remove_project(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    if request.user == project.user:
        models.Project.objects.filter(id=project_id).delete()
        return redirect('all_projects')


@login_required
def edit_project(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    if request.method == "POST":
        project_form = forms.EditProjectForm(data=request.POST, instance=project)
        if project_form.is_valid():
            project_form.save()
            return redirect('all_projects')
    else:
        project_form = forms.EditProjectForm(instance=project)
        return render(request, 'app/edit_project.html', {'form': project_form})
