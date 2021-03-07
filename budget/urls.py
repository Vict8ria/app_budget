from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    # project
    path('create/', views.create_project, name='create_project'),
    path('projects/', views.all_projects, name='all_projects'),
    path('projects/<int:project_id>/', views.detailed_project, name='detailed_project'),
    path('projects/<int:project_id>/remove', views.remove_project, name='remove_project'),
    path('projects/<int:project_id>/edit', views.edit_project, name='edit_project'),

    # login, logout
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # register, profile
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),

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
