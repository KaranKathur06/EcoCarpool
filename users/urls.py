from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views
from django.urls import reverse_lazy

app_name = 'users'

urlpatterns = [
    path('', views.user_list, name='user-list'),
    # Authentication URLs
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile Management URLs
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile-edit'),
    path('profile/delete/', views.delete_account, name='profile-delete'),
    
    # User List (Admin Only)
    path('list/', views.UserListView.as_view(), name='user-list'),
    
    # Password Reset URLs
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='users/password_reset.html',
             email_template_name='users/password_reset_email.html',
             subject_template_name='users/password_reset_subject.txt',
             success_url=reverse_lazy('users:password_reset_done')
         ),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='users/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='users/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ),
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='users/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    # Password Change URLs
    path('password-change/',
         auth_views.PasswordChangeView.as_view(
             template_name='users/password_change.html',
             success_url=reverse_lazy('users:password_change_done')
         ),
         name='password_change'),
    path('password-change/done/',
         auth_views.PasswordChangeDoneView.as_view(
             template_name='users/password_change_done.html'
         ),
         name='password_change_done'),
         
    # API URLs
    path('api/', include('users.api.urls')),

    # New settings URL
    path('settings/', views.SettingsView.as_view(), name='settings'),
]