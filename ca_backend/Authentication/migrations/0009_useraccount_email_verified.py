# Generated by Django 3.2.12 on 2023-11-04 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0008_auto_20231030_1907'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='email_verified',
            field=models.BooleanField(default=False),
        ),
    ]
