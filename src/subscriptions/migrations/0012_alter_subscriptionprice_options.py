# Generated by Django 5.0.8 on 2024-08-20 09:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0011_subscriptionprice_featured_subscriptionprice_order_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptionprice',
            options={'ordering': ['order', 'featured', '-updated']},
        ),
    ]
