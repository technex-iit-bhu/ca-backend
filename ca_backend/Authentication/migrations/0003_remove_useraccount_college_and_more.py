# Generated by Django 4.2.6 on 2023-10-17 13:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Authentication', '0002_useraccount_points'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='useraccount',
            name='college',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='date_joined',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='phone_no',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='pin_code',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='points',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='postal_address',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='role',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='status',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='were_you_ca',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='whatsapp_no',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='why_choose',
        ),
        migrations.RemoveField(
            model_name='useraccount',
            name='year',
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_joined', models.DateTimeField(auto_now_add=True, verbose_name='date joined')),
                ('status', models.CharField(choices=[('P', 'Pending'), ('V', 'Verified'), ('D', 'Deleted')], default='P', max_length=1)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('college', models.CharField(max_length=200)),
                ('year', models.IntegerField()),
                ('phone_no', models.CharField(max_length=10)),
                ('whatsapp_no', models.CharField(max_length=10)),
                ('postal_address', models.TextField()),
                ('pin_code', models.IntegerField()),
                ('why_choose', models.TextField()),
                ('were_you_ca', models.BooleanField(default=False)),
                ('points', models.IntegerField(default=0)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
