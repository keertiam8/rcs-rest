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



class RegisterAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)

            if not serializer.is_valid():
                return Response({
                    "status": 400,
                    "message": "Something went wrong",
                  
                })

            user = serializer.save()

            send_otp_via_email(user.email)

            return Response({
                "status": 200,
                "message": "User registered successfully",
              
            })

        except Exception as e:
            print(e)
            return Response({
                "status": 500,
                "message": "Internal server error",
                
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
                })

            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = User.objects.filter(email=email).first()
            if not user:
                return Response({
                    "status": 400,
                    "message": "Invalid email",
                })

            if not user.check_password(password):
                return Response({
                    "status": 400,
                    "message": "Invalid password",
                })

            # Send OTP to user
            send_otp_via_email(user.email)

            return Response({
                "status": 200,
                "message": "OTP sent successfully"
            })
        except Exception as e:
            print("LOGIN ERROR:", e)
            return Response({
                "status": 500,
                "message": "Internal server error",
            })
        


class OTPVerificationAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"message": "Invalid data"},
                status=400
            )

        email = serializer.validated_data["email"]
        otp = serializer.validated_data["otp"]

        OTP_EXPIRY_TIME = timedelta(minutes=5)

        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"message": "User not found"}, status=400)

        if user.otp != otp:
            return Response({"message": "Invalid OTP"}, status=400)

        if timezone.now() > user.otp_created_at + OTP_EXPIRY_TIME:
            return Response({"message": "OTP expired"}, status=400)

        user.is_verified = True
        user.otp = None
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Login successful",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=200)


class ResendOTPAPI(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            email = request.data.get('email')
            
            if not email:
                return Response({
                    "status": 400,
                    "message": "Email is required",
                    
                })
            
            user = User.objects.filter(email=email).first()
            
            if not user:
                return Response({
                    "status": 400,
                    "message": "User not found",
                   
                })
            
            send_otp_via_email(user.email)
            
            return Response({
                "status": 200,
                "message": "OTP sent successfully",
            })
            
        except Exception as e:
            print("RESEND OTP ERROR:", e)
            return Response({
                "status": 500,
                "message": "Internal server error",
               
            })
                        