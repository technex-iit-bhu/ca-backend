# Generated by Django 3.2.12 on 2023-12-16 09:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0011_merge_20231204_1617'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserPasswordForgotOTP',
        ),
    ]
