from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    
    # Password Reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password-reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password-reset-done'),
    path('password-reset-confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password-reset-complete'),
]
