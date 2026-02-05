from django.db import models
import uuid
from django.db import models
from accounts.models import User


class Business(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="businesses")
    email = models.EmailField()
    name = models.CharField(max_length=255)
    phone_number_id = models.CharField(max_length=255, null=True, blank=True) # WhatsApp Business phone number ID
    google_review_url = models.URLField(null=True, blank=True)
    subscription_plan = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name="locations")
    location_name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.business.name} - {self.location_name}"

class QRCode(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="qr_codes")
    slug = models.SlugField(unique=True) #could remove only tells which part of the cafe the qr code is from ex - table, billing counter
    message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.slug
    
class QRCodeScan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    qr_code = models.ForeignKey(
        QRCode,
        on_delete=models.CASCADE,
        related_name="scans"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Scan of {self.qr_code.slug} at {self.created_at}"

class Feedback(models.Model):
    RATING_CHOICES = [
        ("great", "Great"),
        ("okay", "Okay"),
        ("not_good", "Not Good"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.ForeignKey(QRCode, on_delete=models.CASCADE, related_name="feedbacks")
    customer_phone_number = models.CharField(max_length=20)
    rating = models.CharField(max_length=20, choices=RATING_CHOICES)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.rating} - {self.qr_code.slug}"
