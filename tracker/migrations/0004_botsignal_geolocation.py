from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0003_botsignal'),
    ]

    operations = [
        migrations.AddField(
            model_name='botsignal',
            name='asn',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='botsignal',
            name='city',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='botsignal',
            name='country',
            field=models.CharField(blank=True, max_length=64),
        ),
        migrations.AddField(
            model_name='botsignal',
            name='isp',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddIndex(
            model_name='botsignal',
            index=models.Index(fields=['country', 'timestamp'], name='tracker_bot_country_idx'),
        ),
    ]
