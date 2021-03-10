from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from datetime import date, datetime
from django.core.mail import send_mail
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.db.models import DateField
from django.db.models import Count

from . import forms
from . import models
from . import constants


# Create your views here.
def landing(request):
    return render(request, "landing/index.html")


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
    return render(request, 'registration/profile.html', {'user': request.user})


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
    return render(request, "project/projects.html", {"projects": projects, "today": today})


@login_required
def detailed_project(request, project_id, year=date.today().year, month=date.today().month):
    project = get_object_or_404(models.Project, id=project_id)
    transactions = models.Transaction.objects.filter(
        project=project,
        owner=request.user,
        date__year=year,
        date__month=month,
    )

    report = models.Transaction.objects \
        .annotate(month=TruncMonth('date', output_field=DateField())) \
        .values('month') \
        .annotate(amount=Sum('amount'))\
        .filter(date__year=year, date__month=month)

    report_types = models.Transaction.objects \
        .annotate(month=TruncMonth('date', output_field=DateField())) \
        .values('month', 'transaction_type') \
        .annotate(amount=Sum('amount'))\
        .annotate(dcount=Count('transaction_type'))\
        .filter(date__year=year, date__month=month)

    transaction_form = forms.TransactionForm()

    month_form = forms.MonthsForm()
    selected_date = datetime.strptime(f"{year}-{month}", '%Y-%m')
    month_form.fields['select'].initial = selected_date

    return render(
        request,
        "project/project.html",
        {
            "project": project,
            "transactions": transactions,
            "transaction_types": constants.TRANSACTION_TYPES,
            "report": report[0] if report else '',
            "report_types": report_types if report_types else '',
            "transaction_form": transaction_form,
            "choose_month_form": month_form,
            "year": year,
            "month": month,
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
        return render(request, 'project/create_project.html', {'form': project_form})


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
        return render(request, 'project/edit_project.html', {'form': project_form})


def add_transaction(request, project_id):
    if request.method != "POST":
        return HttpResponse("Bad Request")

    project = models.Project.objects.get(id=project_id)
    transaction_form = forms.TransactionForm(request.POST)

    if transaction_form.is_valid():
        new_transaction = transaction_form.save(commit=False)
        new_transaction.owner = request.user
        new_transaction.project = project
        new_transaction.save()

    return redirect(reverse("detailed_project", args=[project.id]))


def edit_transactions(request, project_id, transaction_id):

    if request.method != "POST":
        return HttpResponse("Bad Request")

    year = request.POST.get("selected_year", "")
    month = request.POST.get("selected_month", "")

    project = models.Project.objects.get(id=project_id)

    if 'remove' in request.POST:
        if request.user == project.owner:
            models.Transaction.objects.filter(id=transaction_id, project=project).delete()

    elif 'save' in request.POST:
        transaction_form = forms.TransactionForm(request.POST)
        if transaction_form.is_valid():
            select = transaction_form.cleaned_data
            print(select)
            transaction = models.Transaction.objects.get(id=transaction_id)
            transaction_form = forms.TransactionForm(request.POST, instance=transaction)
            transaction_form.save()
        else:
            print(transaction_form.errors)

    return redirect(reverse("detailed_project", args=[project.id, year, month]))


def choose_month_project(request, project_id):
    if request.method != "POST":
        return HttpResponse("Bad Request")

    project = models.Project.objects.get(id=project_id)
    if request.user == project.owner:
        form = forms.MonthsForm(request.POST)
        if form.is_valid():
            selected_date = form.cleaned_data['select']
            converted_date = datetime.strptime(selected_date, '%Y-%m-%d %H:%M:%S')
            year, month = converted_date.strftime("%Y"), int(converted_date.strftime("%m"))
            return redirect(reverse("detailed_project", args=[project.id, year, month]))
