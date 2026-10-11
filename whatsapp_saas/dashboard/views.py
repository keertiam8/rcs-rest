from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from .serializer import *
from .models import *
from rest_framework.permissions import IsAuthenticated,AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .emails import *
from .llm_service import analyze_feedback, LLMUnavailable, MAX_COMMENTS
from django.utils.timezone import now as date



# Create your views here.

class FeedbackAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            feedbacks = Feedback.objects.filter(
                qr_code__location__business__owner=request.user
            ).order_by("-created_at")

            serializer = FeedbackSerializer(feedbacks, many=True)

            return Response({
                "data": serializer.data
            })

        except Exception as e:
            print(e)
            return Response({
                "status": 500,
                "message": "Internal server error",
            })
        


class FilteredFeedbackAPI(ListAPIView):
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['rating']

    def get_queryset(self):
        user = self.request.user
        business_id = self.request.query_params.get("business_id")
        location_id = self.request.query_params.get("location_id")
        rating = self.request.query_params.get("rating")
        queryset = Feedback.objects.filter(
            qr_code__location__business__owner=user
        )

        if business_id:
            queryset = queryset.filter(
                qr_code__location__business__id=business_id
            )

        if location_id:
            queryset = queryset.filter(
                qr_code__location__id=location_id
            )
        if rating:
            queryset = queryset.filter(
                rating=rating
            )
        return queryset.order_by("-created_at")
    
class SummaryAPI(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, business_id):
        try:
            total_scans = QRCodeScan.objects.filter(
                qr_code__location__business__owner=request.user,
                qr_code__location__business__id=business_id
            ).count()
        
            feedback_count = Feedback.objects.filter(
                qr_code__location__business__owner=request.user,
                qr_code__location__business__id=business_id
            ).count()

            positive_feedback = Feedback.objects.filter(
                qr_code__location__business__owner=request.user,
                qr_code__location__business__id=business_id,
                rating="great"
            ).count()

            positive_feedback_percentage = 0
            if feedback_count > 0:
                positive_feedback_percentage = (positive_feedback / feedback_count) * 100
                positive_feedback_percentage = round(positive_feedback_percentage, 2)

            return Response({
                "status": 200,
                "message": "Summary fetched successfully",
                "data": {
                    "total_scans": total_scans,
                    "feedback_count": feedback_count,
                    "positive_feedback": positive_feedback,
                    "positive_feedback_percentage": positive_feedback_percentage
                }
            })

        except Exception as e:
            print(e)
            return Response({
                "status": 500,
                "message": "Internal server error",
            })


class AIAnalysisAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, business_id):
        if not Business.objects.filter(id=business_id, owner=request.user).exists():
            return Response({
                "status": 403,
                "message": "Not allowed or business not found"
            })

        queryset = Feedback.objects.filter(
            qr_code__location__business__id=business_id,
            qr_code__location__business__owner=request.user,
        )
        location_id = request.query_params.get("location_id")
        if location_id:
            queryset = queryset.filter(qr_code__location__id=location_id)

        rating_counts = {
            r: queryset.filter(rating=r).count() for r, _ in Feedback.RATING_CHOICES
        }

        with_comments = queryset.exclude(comment__isnull=True).exclude(comment="")
        entries = [
            {
                "location": f.qr_code.location.location_name,
                "rating": f.rating,
                "comment": f.comment,
            }
            for f in with_comments.select_related("qr_code__location").order_by("-created_at")[:MAX_COMMENTS]
        ]

        if not entries:
            return Response({
                "status": 200,
                "message": "No written comments to analyze yet",
                "data": {"rating_counts": rating_counts}
            })

        try:
            analysis = analyze_feedback(rating_counts, entries)
        except LLMUnavailable as e:
            print("AI ANALYSIS ERROR:", e)
            return Response({
                "status": 503,
                "message": "AI model is not available. Make sure Ollama is running."
            })

        return Response({
            "status": 200,
            "message": "Analysis generated",
            "data": {
                "rating_counts": rating_counts,
                "comments_analyzed": len(entries),
                **analysis
            }
        })


class SendSummary(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, business_id):
        business_emails = list(
            Business.objects.filter(
                id=business_id,
                owner=request.user
            ).values_list('email', flat=True)
        )

        if not business_emails:
            return Response({
                "status": 403,
                "message": "Not allowed or business not found"
            })

        total_scans = QRCodeScan.objects.filter(
            qr_code__location__business__id=business_id
        ).count()

        feedback_qs = Feedback.objects.filter(
            qr_code__location__business__id=business_id
        )

        feedback_count = feedback_qs.count()
        positive_feedback = feedback_qs.filter(rating="great").count()

        positive_feedback_percentage = 0
        if feedback_count:
            positive_feedback_percentage = round(
                (positive_feedback / feedback_count) * 100, 2
            )

        report_text = {
            "total_scans": total_scans,
            "feedback_count": feedback_count,
            "positive_feedback": positive_feedback,
            "positive_feedback_percentage": positive_feedback_percentage
        }

        send_summary_via_email(
            business_emails,
            report_text,
            business_id=str(business_id),
            week_range=date().strftime("%Y-%m-%d")
        )

        return Response({
            "status": 200,
            "message": "Summary email sent successfully"
        })
