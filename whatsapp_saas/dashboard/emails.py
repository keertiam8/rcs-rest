
import io
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas


def _build_pdf(report_text):
    """Create a PDF summary and return bytes."""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)

    p.drawString(100, 750, "Weekly Summary Report")
    p.drawString(100, 730, f"Total Scans: {report_text.get('total_scans', 0)}")
    p.drawString(100, 710, f"Feedback Count: {report_text.get('feedback_count', 0)}")
    p.drawString(100, 690, f"Positive Feedback: {report_text.get('positive_feedback', 0)}")
    p.drawString(
        100, 670,
        f"Positive %: {report_text.get('positive_feedback_percentage', 0)}%"
    )

    p.showPage()
    p.save()

    buffer.seek(0)
    pdf_bytes = buffer.read()
    buffer.close()
    return pdf_bytes


def send_summary_via_email(recipient_list, report_text, business_id=None, week_range=None):
    """
    Send weekly summary email with PDF attachment.
    """
    if not recipient_list:
        return

    context = {
        'business_id': business_id,
        'week_range': week_range,
        'total_scans': report_text.get('total_scans', 0),
        'feedback_count': report_text.get('feedback_count', 0),
        'positive_feedback': report_text.get('positive_feedback', 0),
        'positive_feedback_percentage': report_text.get('positive_feedback_percentage', 0),
    }

    try:
        body = render_to_string('report.html', context)
        content_type = 'html'
    except Exception:
        body = (
            f"Weekly Summary\n\n"
            f"Total Scans: {context['total_scans']}\n"
            f"Feedback Count: {context['feedback_count']}\n"
            f"Positive Feedback: {context['positive_feedback']}\n"
            f"Positive %: {context['positive_feedback_percentage']}%\n"
        )
        content_type = 'plain'

    email = EmailMessage(
        subject="Weekly Summary Report",
        body=body,
        from_email=settings.EMAIL_HOST_USER,
        to=recipient_list,
    )

    if content_type == 'html':
        email.content_subtype = 'html'

    try:
        pdf_data = _build_pdf(report_text)
        email.attach('weekly_summary.pdf', pdf_data, 'application/pdf')
    except Exception:
        pass  

    email.send()
