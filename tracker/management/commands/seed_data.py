"""
Management command to seed realistic data for the tracking system.
Generates scenarios:
1. Investor Pitch Deck (VC engagement)
2. Leaked Internal Memo (Viral spread)
3. Proposal Document (Targeted corporate access)
"""
import random
import uuid
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from tracker.models import Document, AccessLog

class Command(BaseCommand):
    help = 'Seeds database with realistic tracking data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')
        
        # Clear existing data
        AccessLog.objects.all().delete()
        Document.objects.all().delete()
        
        self.seed_investor_pitch()
        self.seed_leaked_memo()
        self.seed_proposal()
        
        self.stdout.write(self.style.SUCCESS('Successfully seeded data'))

    def seed_investor_pitch(self):
        """High value, targeted access from VC hubs."""
        doc = Document.objects.create(
            cid=f"pitch-{uuid.uuid4().hex[:8]}",
            name="Series A Pitch Deck (Confidential)",
            metadata={"type": "presentation", "version": "v3.1"}
        )
        
        # Locations: SF, NYC, London, Singapore
        scenarios = [
            ("San Francisco", "United States", "Comcast Cable", "AS7922"),
            ("New York", "United States", "Verizon Fios", "AS701"),
            ("London", "United Kingdom", "British Telecommunications", "AS2856"),
            ("Singapore", "Singapore", "Singtel", "AS7473"),
        ]
        
        # Clients: Mostly desktop, some mobile
        clients = [
            ("Microsoft Office 2021", "Windows 10"),
            ("Microsoft Word", "macOS"),
            ("Chrome 120.0", "macOS"),
            ("Safari 17.2", "iOS"),
        ]
        
        base_time = timezone.now() - timedelta(days=7)
        
        for _ in range(45):
            city, country, isp, asn = random.choice(scenarios)
            client, os = random.choice(clients)
            
            # Skew towards business hours
            hour_offset = random.randint(9, 18)
            day_offset = random.randint(0, 6)
            timestamp = base_time + timedelta(days=day_offset, hours=hour_offset, minutes=random.randint(0, 59))
            
            self._create_log(doc, timestamp, city, country, isp, asn, client, os)

    def seed_leaked_memo(self):
        """Viral spread, diverse IPs, many mobile users."""
        doc = Document.objects.create(
            cid=f"memo-{uuid.uuid4().hex[:8]}",
            name="Internal Memo: 2026 Strategy",
            metadata={"type": "pdf", "sensitivity": "high"}
        )
        
        base_time = timezone.now() - timedelta(days=2)
        
        # Initial leak
        self._create_log(doc, base_time, "Menlo Park", "United States", "Facebook Inc", "AS32934", "Chrome 120.0", "macOS")
        
        # Viral spread
        for i in range(120):
            # Time accelerates
            offset_minutes = int(i ** 1.5)  # Exponential spread
            timestamp = base_time + timedelta(minutes=offset_minutes)
            
            if timestamp > timezone.now():
                break
                
            # diverse countries
            country_data = random.choice([
                ("United States", "Verizon"), ("United Kingdom", "BT"), ("Germany", "Deutsche Telekom"),
                ("India", "Jio"), ("Japan", "Softbank"), ("Brazil", "Vivo")
            ])
            
            client = random.choice(["Chrome Mobile", "Safari Mobile", "Firefox", "Edge"])
            os = random.choice(["Android", "iOS", "Windows 11", "macOS"])
            
            self._create_log(doc, timestamp, "", country_data[0], country_data[1], "AS0000", client, os)

    def seed_proposal(self):
        """Corporate environment, specific IPs repeating."""
        doc = Document.objects.create(
            cid=f"prop-{uuid.uuid4().hex[:8]}",
            name="Enterprise License Proposal - Acme Corp",
            metadata={"client": "Acme Corp"}
        )
        
        base_time = timezone.now() - timedelta(days=14)
        
        # Decision makers coming back to the doc
        viewers = [
            ("192.168.1.5", "Chrome 119", "Windows 10"), # Procurement
            ("10.0.0.42", "Microsoft Word", "Windows 11"), # CTO
            ("172.16.2.8", "Safari 17", "macOS"), # CEO
        ]
        
        for viewer_ip, client, os in viewers:
            # Each viewer looks 3-5 times
            for _ in range(random.randint(3, 5)):
                day_offset = random.randint(1, 14)
                timestamp = base_time + timedelta(days=day_offset, hours=random.randint(8, 20))
                
                self._create_log(
                    doc, timestamp, "Austin", "United States", 
                    "Acme Corp Network", "AS64496", client, os, ip=viewer_ip
                )

    def _create_log(self, doc, timestamp, city, country, isp, asn, client, os, ip=None):
        if not ip:
            ip = f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            
        AccessLog.objects.create(
            document=doc,
            cid=doc.cid,
            timestamp=timestamp,
            ip_address=ip,
            country=country,
            city=city,
            isp=isp,
            asn=asn,
            client_app=client,
            os_name=os.split()[0],
            os_version=os.split()[1] if len(os.split()) > 1 else "",
            browser_name=client.split()[0],
            endpoint=f"/assets/media/logo.png",
            method="GET",
            is_first_access=random.random() < 0.3
        )
