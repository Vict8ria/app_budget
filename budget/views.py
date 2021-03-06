from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

from . import forms
from . import models

# Create your views here.
def landing(request):
    return render(request, "landing/index.html")


def dashboard(request):
    return render(request, "app/dashboard.html")


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
