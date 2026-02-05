from django.urls import path
from . import views


urlpatterns = [path("data/", views.WhatsAppWebhookView.as_view(), name="whatsapp-webhook") ]