# Generated by Django 5.0.8 on 2024-08-20 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0017_remove_subscriptionprice_features_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usersubscription',
            name='stripe_id',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]