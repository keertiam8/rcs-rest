from datetime import timedelta
from django.shortcuts import render
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UserSerializer, LoginSerializer, VerifyOTPSerializer
from .emails import *
from  rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User



# Create your views here.
class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    "status": 400,
                    "message": "Something went wrong",
                    "data": serializer.errors
                })

            user = serializer.save()

            send_otp_via_email(user.email)

            return Response({
                "status": 200,
                "message": "User registered successfully",
                "data": {
                    "email": user.email
                }
            })

        except Exception as e:
            print(e)
            return Response({
                "status": 500,
                "message": "Internal server error",
                "data": str(e)
            })

        


class LoginVerification(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    "status": 400,
                    "message": "Invalid data",
                    "data": serializer.errors
                })

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = User.objects.filter(email=email).first()
            if not user:
                return Response({
                    "status": 400,
                    "message": "Invalid email",
                    "data": {}
                })

            if not user.check_password(password):
                return Response({
                    "status": 400,
                    "message": "Invalid password",
                    "data": {}
                })

            # Send OTP to user
            send_otp_via_email(user.email)

            return Response({
                "status": 200,
                "message": "OTP sent successfully",
                "data": {
                    "email": user.email
                }
            })
        except Exception as e:
            print("LOGIN ERROR:", e)
            return Response({
                "status": 500,
                "message": "Internal server error",
                "data": str(e)
            })

class OTPVerificationAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = VerifyOTPSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    "status": 400,
                    "message": "Invalid data",
                    "data": serializer.errors
                })

            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            OTP_EXPIRY_TIME = timedelta(minutes=5)
            user = User.objects.filter(email=email).first()

            if not user:
                return Response({
                    "status": 400,
                    "message": "Invalid email",
                    "data": {}
                })

            if user.otp != otp:
                return Response({
                    "status": 400,
                    "message": "Invalid OTP",
                    "data": {}
                })

            if timezone.now() > user.otp_created_at + OTP_EXPIRY_TIME:
                return Response({
                    "status": 400,
                    "message": "OTP expired",
                    "data": {}
                })

            # Mark user as verified (OTP will be cleared when JWT is issued)
            user.is_verified = True
            user.save()
            user_serializer = UserSerializer(user)
            return Response({
                "status": 200,
                "message": "Login successful",
                "data": user_serializer.data
            })
        except Exception as e:
            print("LOGIN ERROR:", e)
            return Response({
                "status": 500,
                "message": "Internal server error",
                "data": str(e)
            })


        
class CustomTokenObtainPairView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        user = User.objects.filter(email=email).first()

        if not user:
            return Response({"message": "User not found"}, status=400)

        if user.otp != otp:
            return Response({"message": "Invalid OTP"}, status=400)

        # OTP is valid → issue JWT
        refresh = RefreshToken.for_user(user)

        # clear OTP
        user.otp = None
        user.save()

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })             


class ResendOTPAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            
            if not email:
                return Response({
                    "status": 400,
                    "message": "Email is required",
                    "data": {}
                })
            
            user = User.objects.filter(email=email).first()
            
            if not user:
                return Response({
                    "status": 400,
                    "message": "User not found",
                    "data": {}
                })
            
            # Send new OTP
            send_otp_via_email(user.email)
            
            return Response({
                "status": 200,
                "message": "OTP sent successfully",
                "data": {
                    "email": user.email
                }
            })
            
        except Exception as e:
            print("RESEND OTP ERROR:", e)
            return Response({
                "status": 500,
                "message": "Internal server error",
                "data": str(e)
            })
                        