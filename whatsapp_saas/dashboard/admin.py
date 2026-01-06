from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Business, Location, QRCode, Feedback



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
    list_display = ("id", "rating", "phone_number", "created_at")