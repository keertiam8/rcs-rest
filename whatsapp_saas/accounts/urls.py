from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='register'), 
    path('login-verification/', views.LoginVerification.as_view(), name='verify'),
    path('otp-verification/', views.OTPVerificationAPI.as_view(), name='otp-verification'), 
    path('resend-otp/', views.ResendOTPAPI.as_view(), name='resend-otp'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    
]   