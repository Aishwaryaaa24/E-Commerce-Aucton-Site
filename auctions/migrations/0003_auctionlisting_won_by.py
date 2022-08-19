# Generated by Django 4.0.6 on 2022-08-06 04:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0002_auctionlisting_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='auctionlisting',
            name='won_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
