from django.core.management.base import BaseCommand

from tracker.models import AccessLog, BotSignal
from tracker.utils.geolocation import enrich_instance_geo, get_geo_for_ip, is_private_ip


class Command(BaseCommand):
    help = 'Backfill geolocation fields (including coordinates) from stored IP addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without saving',
        )
        parser.add_argument(
            '--model',
            choices=('all', 'events', 'signals'),
            default='all',
            help='Which records to backfill',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        model_choice = options['model']
        updated = 0

        if model_choice in ('all', 'events'):
            updated += self._backfill_queryset(
                AccessLog.objects.filter(latitude__isnull=True).exclude(ip_address__isnull=True),
                lambda record: record.ip_address,
                dry_run,
                'AccessLog',
            )

        if model_choice in ('all', 'signals'):
            updated += self._backfill_queryset(
                BotSignal.objects.filter(latitude__isnull=True).exclude(source_ip__isnull=True),
                lambda record: record.source_ip,
                dry_run,
                'BotSignal',
            )

        action = 'Would update' if dry_run else 'Updated'
        self.stdout.write(self.style.SUCCESS(f'{action} {updated} record(s)'))

    def _backfill_queryset(self, queryset, ip_getter, dry_run, label):
        updated = 0
        for record in queryset.iterator():
            ip = ip_getter(record)
            if is_private_ip(ip):
                continue

            geo = get_geo_for_ip(ip)
            if geo.get('latitude') is None:
                continue

            if dry_run:
                self.stdout.write(
                    f'[{label}] {record.id} ({ip}): '
                    f'{geo.get("city")}, {geo.get("country")} '
                    f'[{geo.get("latitude")}, {geo.get("longitude")}]'
                )
            elif enrich_instance_geo(record, ip):
                updated += 1

        return updated
