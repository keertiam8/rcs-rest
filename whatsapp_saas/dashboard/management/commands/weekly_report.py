from django.core.management.base import BaseCommand
from django.utils.timezone import now
from datetime import timedelta

from dashboard.models import Business, QRCodeScan, Feedback
from dashboard.emails import send_summary_via_email


class Command(BaseCommand):
    help = "Send weekly email report to all businesses"

    def handle(self, *args, **kwargs):
        businesses = Business.objects.all()

        if not businesses.exists():
            self.stdout.write(self.style.WARNING("No businesses found"))
            return

        end_date = now().date()
        start_date = end_date - timedelta(days=7)
        week_range = f"{start_date} to {end_date}"

        for business in businesses:
            try:
                business_emails = [business.email]

                total_scans = QRCodeScan.objects.filter(
                    qr_code__location__business=business,
                    created_at__gte=start_date,
                    created_at__lte=end_date
                ).count()

                feedback_qs = Feedback.objects.filter(
                    qr_code__location__business=business,
                    created_at__gte=start_date,
                    created_at__lte=end_date
                )

                feedback_count = feedback_qs.count()
                positive_feedback = feedback_qs.filter(rating="great").count()

                positive_feedback_percentage = (
                    (positive_feedback / feedback_count) * 100
                    if feedback_count else 0
                )

                report_text = {
                    "total_scans": total_scans,
                    "feedback_count": feedback_count,
                    "positive_feedback": positive_feedback,
                    "positive_feedback_percentage": round(positive_feedback_percentage, 2),
                }

                send_summary_via_email(
                    business_emails,
                    report_text,
                    business_id=str(business.id),
                    week_range=week_range
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"✓ Weekly report sent to {business.name} ({business.email})"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ Failed for {business.name}: {str(e)}"
                    )
                )

        self.stdout.write(self.style.SUCCESS("✓ Weekly report job completed"))
