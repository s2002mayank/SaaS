# Generated by Django 5.0.8 on 2024-08-14 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('visits', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagevisits',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
