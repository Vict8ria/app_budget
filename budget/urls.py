from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.landing, name='main'),

    # projects
    path('projects/', views.all_projects, name='all_projects'),
    path('projects/create/', views.create_project, name='create_project'),
    path('projects/<int:project_id>/<int:year>/<int:month>/', views.detailed_project, name='detailed_project'),
    path('projects/<int:project_id>/<int:year>/', views.detailed_project, name='detailed_project'),
    path('projects/<int:project_id>/', views.detailed_project, name='detailed_project'),
    path('projects/<int:project_id>/remove/', views.remove_project, name='remove_project'),
    path('projects/<int:project_id>/edit/', views.edit_project, name='edit_project'),
    path('projects/<int:project_id>/month/', views.choose_month_project, name='choose_month_project'),

    # transactions
    path('projects/<int:project_id>/transactions/', views.add_transaction, name='add_transaction'),
    path('projects/<int:project_id>/<int:transaction_id>/edit/', views.edit_transactions, name='edit_transactions'),

    # login, logout
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # register, profile
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

    # contact us
    path('contact_us/', views.contact_us, name='contact_us'),

    # reset password
    path('password_reset/', auth_views.PasswordResetView.as_view(
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
]
