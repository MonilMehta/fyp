from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0004_botsignal_geolocation'),
    ]

    operations = [
        migrations.AddField(
            model_name='accesslog',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='accesslog',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='botsignal',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='botsignal',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
