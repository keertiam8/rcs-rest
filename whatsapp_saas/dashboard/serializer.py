from rest_framework import routers, serializers, viewsets

from .models import Feedback

class FeedbackSerializer(serializers.ModelSerializer):
    business_name = serializers.CharField(
        source="qr_code.location.business.name",
        read_only=True
    )
    location_name = serializers.CharField(
        source="qr_code.location.location_name",
        read_only=True
    )

    class Meta:
        model = Feedback
        fields = [
            "id",
            "business_name",
            "location_name",
            "rating",
            "comment",
            "created_at",
        ]


