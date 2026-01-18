from django.urls import path
from . import views

urlpatterns = [
    path('feedback/', views.FeedbackAPI.as_view(), name='dashboard_home'),
    path('filtered_feedback/', views.FilteredFeedbackAPI.as_view(), name='filtered_feedback'),
    path('summary_feedback/<uuid:business_id>/', views.SummaryAPI.as_view(), name='summary_feedback'),
    path('send_summary_email/<uuid:business_id>/', views.SendSummary.as_view(), name='send_summary_email'),
]