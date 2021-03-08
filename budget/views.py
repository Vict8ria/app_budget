from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from datetime import date
from django.core.mail import send_mail
from django.db.models import Sum
from django.db.models.functions import TruncMonth, Cast, Substr
from django.db.models import DateField, CharField

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


def contact_us(request):
    sent = False

    if request.method == "POST":
        form = forms.ContactUsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            subject = "Budget app: Contact us"
            body = {
                'first_name': cd['name'],
                'email': cd['email'],
                'phone': cd['phone'].as_e164,
                'message': cd['message'],
            }
            message = "\n".join(body.values())
            from_email = body["email"]
            send_mail(subject, message, from_email, ['vict8ria.k@gmail.com'])
            sent = True
    else:
        form = forms.ContactUsForm()

    return render(request, 'contact_us/contact_us.html', {'form': form, 'sent': sent})


@login_required
def all_projects(request):
    today = date.today()
    projects = models.Project.objects.filter(owner=request.user)
    return render(request, "app/project/projects.html", {"projects": projects, "today": today})


@login_required
def detailed_project(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    transactions = models.Transaction.objects.all()
    current_date = date.today().strftime('%Y-%m')

    report = models.Transaction.objects.annotate(
        month=Substr(Cast(TruncMonth('date', output_field=DateField()), output_field=CharField()), 1, 7)
    ).values('month').annotate(amount=Sum('amount'))

    transaction_form = forms.TransactionForm()

    return render(
        request,
        "app/project/project.html",
        {
            "project": project,
            "transactions": transactions,
            "report": list(report),
            "transaction_form": transaction_form
        }
    )


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
            return HttpResponse("Data is not valid")
    else:
        project_form = forms.CreateProjectForm()
        return render(request, 'app/project/create_project.html', {'form': project_form})


@login_required
def remove_project(request, project_id):
    project = get_object_or_404(models.Project, id=project_id)
    if request.user == project.owner:
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
        return render(request, 'app/project/edit_project.html', {'form': project_form})


def add_transaction(request, project_id):
    if request.method == "POST":
        project = models.Project.objects.get(id=project_id)
        transaction_form = forms.TransactionForm(request.POST)

        if transaction_form.is_valid():
            new_transaction = transaction_form.save(commit=False)
            new_transaction.owner = request.user
            new_transaction.project = project
            new_transaction.save()

            return redirect(reverse("detailed_project", args=[project.id]))
    else:
        return HttpResponse("Bad Request")


def edit_transactions(request, project_id, transaction_id):
    if request.method != "POST":
        return HttpResponse("Bad Request")

    project = models.Project.objects.get(id=project_id)

    if 'remove' in request.POST:
        if request.user == project.owner:
            models.Transaction.objects.filter(id=transaction_id, project=project).delete()

    elif 'save' in request.POST:
        transaction_form = forms.TransactionForm(request.POST)
        if transaction_form.is_valid():
            transaction = models.Transaction.objects.get(id=transaction_id)
            transaction_form = forms.TransactionForm(request.POST, instance=transaction)
            transaction_form.save()

    return redirect(reverse("detailed_project", args=[project.id]))
