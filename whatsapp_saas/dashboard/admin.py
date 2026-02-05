from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Business, Location, QRCode, Feedback


#controls what appears in the admin panel 
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "email", "subscription_plan")

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("id", "location_name", "business")

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ("id", "slug", "location")

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "rating", "customer_phone_number", "created_at")