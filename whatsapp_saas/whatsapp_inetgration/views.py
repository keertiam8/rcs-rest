from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from dashboard.models import QRCode, Feedback, Business

class WhatsAppWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        payload = request.data

        try:
            value = payload["entry"][0]["changes"][0]["value"]

            if "messages" not in value:
                return Response({"status": "ignored"})

            message = value["messages"][0]

           
            customer_phone = message["from"]

            phone_number_id = value["metadata"]["phone_number_id"]

            interactive = message.get("interactive")

            if not interactive:
                return Response({"status": "no interactive reply"})

            
            if "button_reply" in interactive:
                rating = interactive["button_reply"]["id"]

            elif "list_reply" in interactive:
                rating = interactive["list_reply"]["id"]

            else:
                return Response({"error": "Invalid interactive reply"}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=400)

        #Find Business
        business = Business.objects.filter(
            phone_number_id=phone_number_id
        ).first()

        if not business:
            return Response({"error": "Business not found"}, status=400)

        #rn picking the first qr under business
        qr_code = QRCode.objects.filter(
            location__business=business
        ).first()

        if not qr_code:
            return Response({"error": "QR Code not found"}, status=400)

        #store Feedback
        Feedback.objects.create(
            qr_code=qr_code,
            customer_phone_number=customer_phone,
            rating=rating
        )

        return Response({
            "status": "200",
            "message": "feedback saved"
            })