import random
from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from accounts.models import User
from dashboard.models import Business, Feedback, Location, QRCode, QRCodeScan

BUSINESS_NAME = "Demo Cafe"
PHONE_NUMBER_ID = "TEST_PHONE_ID_001"

LOCATIONS = {
    "Whitefield": {
        "address": "ITPL Main Road, Whitefield, Bengaluru",
        "slugs": ["whitefield-table-1", "whitefield-counter"],
        "feedback": [
            ("not_good", "Waited 25 minutes for a coffee, the staff looked overwhelmed"),
            ("not_good", "Table was sticky and nobody cleaned it before we sat down"),
            ("not_good", "Service was really slow at lunch, only two people at the counter"),
            ("not_good", "Ordered at 1pm and food came at 1:40. Not acceptable"),
            ("okay", "Food was fine but we had to ask three times for water"),
            ("okay", "Coffee was good, billing took forever though"),
            ("okay", "Nice ambience but the washroom needs cleaning"),
            ("great", "Loved the cold brew and the music"),
            ("great", "Great place to work from, fast wifi"),
            ("great", "Pasta was excellent"),
        ],
    },
    "Indiranagar": {
        "address": "100 Feet Road, Indiranagar, Bengaluru",
        "slugs": ["indiranagar-table-1", "indiranagar-counter"],
        "feedback": [
            ("not_good", "The sandwich arrived cold and it felt overpriced"),
            ("not_good", "Very noisy at lunch, could not hold a conversation"),
            ("okay", "Nice place but a bit pricey for the portion size"),
            ("okay", "Food was lukewarm when it reached the table"),
            ("great", "Staff were super friendly and service was quick"),
            ("great", "Best croissants in the area"),
            ("great", "Loved the latte art and the staff remembered my name"),
            ("great", "Quick service even when it was busy"),
            ("great", "Cozy seating and great coffee"),
            ("great", "Brownie was amazing"),
        ],
    },
}


class Command(BaseCommand):
    help = "Create a demo business with locations, QR codes, scans and feedback for an existing user."

    def add_arguments(self, parser):
        parser.add_argument("--email", required=True, help="Email of an already registered user")
        parser.add_argument("--reset", action="store_true", help="Delete the existing demo business first")

    def handle(self, *args, **opts):
        try:
            owner = User.objects.get(email=opts["email"])
        except User.DoesNotExist:
            raise CommandError(f"No user with email {opts['email']}. Register through /accounts/register/ first.")

        existing = Business.objects.filter(owner=owner, name=BUSINESS_NAME)
        if existing.exists():
            if not opts["reset"]:
                raise CommandError("Demo business already exists. Re-run with --reset to rebuild it.")
            existing.delete()

        business = Business.objects.create(
            owner=owner,
            email=owner.email,
            name=BUSINESS_NAME,
            phone_number_id=PHONE_NUMBER_ID,
            subscription_plan="free",
        )

        rng = random.Random(7)
        now = timezone.now()
        total_feedback = 0

        for loc_name, cfg in LOCATIONS.items():
            location = Location.objects.create(business=business, location_name=loc_name, address=cfg["address"])
            qrs = [
                QRCode.objects.create(location=location, slug=s, message="How was your visit today?")
                for s in cfg["slugs"]
            ]

            for qr in qrs:
                for _ in range(rng.randint(12, 20)):
                    scan = QRCodeScan.objects.create(qr_code=qr)
                    QRCodeScan.objects.filter(pk=scan.pk).update(
                        created_at=now - timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 12))
                    )

            for i, (rating, comment) in enumerate(cfg["feedback"]):
                fb = Feedback.objects.create(
                    qr_code=qrs[i % len(qrs)],
                    customer_phone_number=f"9198{rng.randint(10000000, 99999999)}",
                    rating=rating,
                    comment=comment,
                )
                Feedback.objects.filter(pk=fb.pk).update(
                    created_at=now - timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 12))
                )
                total_feedback += 1

        self.stdout.write(self.style.SUCCESS(
            f"Seeded '{BUSINESS_NAME}' (id {business.id}) for {owner.email}: "
            f"{len(LOCATIONS)} locations, {total_feedback} feedback rows with comments."
        ))
        self.stdout.write(f"Business id for API calls: {business.id}")
