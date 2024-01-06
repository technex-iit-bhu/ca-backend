# Generated by Django 3.2.12 on 2024-01-06 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Task', '0007_merge_20231229_1835'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='task',
            name='title',
            field=models.CharField(max_length=255),
        ),
    ]