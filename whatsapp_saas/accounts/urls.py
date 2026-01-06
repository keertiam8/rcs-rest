from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', views.RegisterAPI.as_view(), name='register'), 
    path('verify/', views.LoginVerification.as_view(), name='verify'),
    path('otp-verification/', views.OTPVerificationAPI.as_view(), name='otp-verification'), 
    path('resend-otp/', views.ResendOTPAPI.as_view(), name='resend-otp'),
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    
]   