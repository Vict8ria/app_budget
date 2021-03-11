from datetime import date, datetime
from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.db.models import DateField
from django.db.models import Count
from django.http import HttpResponse
from django.urls import reverse
from django.core.mail import send_mail

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
            print(form.errors)
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
            send_mail(subject, message, from_email, [constants.EMAIL_ADMIN])
            sent = True
    else:
        form = forms.ContactUsForm()

    return render(request, 'contact_us/contact_us.html', {'form': form, 'sent': sent})


@login_required
def all_projects(request):
    today = date.today()
    projects = models.Project.objects.filter(owner=request.user)
    return render(request, "project/projects.html", {"projects": projects, "today": today})


def prepare_report(project, year, month):
    report_by_month_amount = models.Transaction.objects \
        .annotate(month=TruncMonth('date', output_field=DateField())) \
        .values('month') \
        .annotate(amount=Sum('amount')) \
        .filter(date__year=year, date__month=month, project=project)

    report_by_types = models.Transaction.objects \
        .annotate(month=TruncMonth('date', output_field=DateField())) \
        .values('month', 'transaction_type') \
        .annotate(amount=Sum('amount')) \
        .annotate(dcount=Count('transaction_type')) \
        .filter(date__year=year, date__month=month, project=project)

    report_amount = [i.get("amount") for i in report_by_types]
    report_types = [i.get("transaction_type") for i in report_by_types]
    amount = [i.get("amount") for i in report_by_month_amount]

    return {
        'month_amount': amount[0] if amount else 0,
        'amount': report_amount,
        'types': report_types
    }


@login_required
def detailed_project(request, project_id, year=date.today().year, month=date.today().month):
    project = get_object_or_404(models.Project, id=project_id)

    transactions = models.Transaction.objects.filter(
        project=project,
        owner=request.user,
        date__year=year,
        date__month=month,
    ).order_by('date')

    report = prepare_report(project, year, month)

    transaction_form = forms.TransactionForm()
    month_form = forms.MonthsForm()

    selected_date = datetime.strptime(f"{year}-{month}", '%Y-%m')
    transaction_form.fields['date'].initial = selected_date
    month_form.fields['select'].initial = selected_date

    return render(
        request,
        "project/project.html",
        {
            "project": project,
            "transactions": transactions,
            "transaction_types": constants.TRANSACTION_TYPES,
            "report": report,
            "transaction_form": transaction_form,
            "choose_month_form": month_form,
            "year": year,
            "month": month,
        }
    )


@login_required
def create_project(request):
    if request.method == "POST":
        form = forms.ProjectForm(request.POST)
        if form.is_valid():
            new_project = form.save(commit=False)
            new_project.owner = request.user
            new_project.save()
            return redirect(reverse("detailed_project", args=[new_project.id]))
        else:
            print(form.errors)
    else:
        form = forms.ProjectForm()

    return render(request, 'project/create_project.html', {'form': form})


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
        form = forms.ProjectForm(data=request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('all_projects')
        else:
            print(form.errors)
    else:
        form = forms.ProjectForm(instance=project)

    return render(request, 'project/edit_project.html', {'form': form})


def add_transaction(request, project_id):
    if request.method != "POST":
        return HttpResponse("Bad Request")

    year = request.POST.get("selected_year", "")
    month = request.POST.get("selected_month", "")

    project = models.Project.objects.get(id=project_id)
    form = forms.TransactionForm(request.POST)

    if form.is_valid():
        new_transaction = form.save(commit=False)
        new_transaction.owner = request.user
        new_transaction.project = project
        new_transaction.save()
        print(new_transaction)
    else:
        print(form.errors)

    return redirect(reverse("detailed_project", args=[project.id, year, month]))


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
    form = forms.MonthsForm(request.POST)

    if form.is_valid():
        selected_date = form.cleaned_data['select']
        converted_date = datetime.strptime(selected_date, '%Y-%m-%d %H:%M:%S')
        year, month = converted_date.strftime("%Y"), int(converted_date.strftime("%m"))
        return redirect(reverse("detailed_project", args=[project.id, year, month]))
