# Generated by Django 5.0.8 on 2024-08-21 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0022_alter_usersubscription_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='cancel_at_period_end',
            field=models.BooleanField(default=False),
        ),
    ]
