# Generated by Django 3.2.12 on 2023-12-29 12:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Task', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='incentives',
            field=models.TextField(blank=True),
        ),
    ]