# Generated by Django 3.2.12 on 2023-10-20 21:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0005_useraccount_referral_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='role',
            field=models.IntegerField(choices=[(3, 'Admin'), (2, 'Staff'), (1, 'User')], default=1),
        ),
    ]
