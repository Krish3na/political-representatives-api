from django.core.management.base import BaseCommand
from django.db import transaction
from legislators.models import Legislator
import requests
import csv
from io import StringIO
import os
from datetime import datetime

def parse_date(date_str):
    if not date_str:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    return None

class Command(BaseCommand):
    help = "Ingest legislators data into the legislators table"

    def add_arguments(self, parser):
        parser.add_argument("--truncate", action="store_true", help="Clear existing data before ingesting")

    def handle(self, *args, **options):
        csv_url = os.environ.get("LEGISLATORS_CSV_URL")

        self.stdout.write(self.style.NOTICE(f"Downloading: {csv_url}"))
        resp = requests.get(csv_url, timeout=30)
        resp.raise_for_status()

        f = StringIO(resp.text)
        reader = csv.DictReader(f)

        with transaction.atomic():
            if options.get("truncate"):
                self.stdout.write(self.style.WARNING("Truncating existing data..."))
                Legislator.objects.all().delete()

            added = 0
            skipped = 0

            for row in reader:
                try:
                    govtrack_id = int(row.get("govtrack_id", 0))
                    if not govtrack_id:
                        skipped += 1
                        continue

                    first_name = (row.get("first_name") or "").strip()
                    last_name = (row.get("last_name") or "").strip()
                    birthday = parse_date((row.get("birthday") or "").strip())
                    gender = (row.get("gender") or "").strip()
                    type_val = (row.get("type") or "").strip()
                    state = (row.get("state") or "").strip()
                    district = (row.get("district") or "").strip() or None
                    party = (row.get("party") or "").strip()
                    url = (row.get("url") or "").strip()

                    # required fields
                    if not all([first_name, last_name, birthday, gender, type_val, state, party]):
                        skipped += 1
                        continue

                    # Upsert
                    Legislator.objects.update_or_create(
                        govtrack_id=govtrack_id,
                        defaults={
                            "first_name": first_name,
                            "last_name": last_name,
                            "birthday": birthday,
                            "gender": gender,
                            "type": type_val,
                            "state": state,
                            "district": district,
                            "party": party,
                            "url": url or "",
                            "notes": None,
                        },
                    )
                    added += 1

                    if added % 100 == 0:
                        self.stdout.write(self.style.NOTICE(f"Processed {added} records..."))

                except Exception as e:
                    skipped += 1
                    continue

        self.stdout.write(self.style.SUCCESS(f"Ingestion complete. Added/Updated: {added}, Skipped: {skipped}"))