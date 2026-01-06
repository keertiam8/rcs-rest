import random
from django.core.mail import send_mail,EmailMessage
from django.conf import settings
from .models import User
from django.utils import timezone
from .views import SummaryAPI
import io
from reportlab.pdfgen import canvas


report_text = SummaryAPI.get("data")



   
def send_summary_via_email(recipient_list, report_text):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 750, "Summary Report")
    p.drawString(100, 730, f"Total Scans: {report_text.get('total_scans', 0)}")
    p.drawString(100, 710, f"Feedback Count: {report_text.get('feedback_count', 0)}")
    p.drawString(100, 690, f"Positive Feedback: {report_text.get('positive_feedback', 0)}")
    p.drawString(100, 670, f"Positive %: {report_text.get('positive_feedback_percentage', 0)}%")
    p.showPage()
    p.save()
    buffer.seek(0)

    subject = 'Weekly Report'
    message = 'Here is your weekly report. Please see the attached PDF.'
    email_from = settings.EMAIL_HOST_USER

    mail = EmailMessage(subject, message, email_from, recipient_list)
    mail.attach('summary.pdf', buffer.read(), 'application/pdf')
    mail.send()