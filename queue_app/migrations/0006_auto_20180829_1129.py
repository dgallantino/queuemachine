# Generated by Django 2.1 on 2018-08-29 11:29

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('queue_app', '0005_auto_20180829_1118'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='queue',
            options={'ordering': ['-date_created']},
        ),
        migrations.RemoveField(
            model_name='queue',
            name='created',
        ),
        migrations.AddField(
            model_name='queue',
            name='call_flag',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='queue',
            name='date_created',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='queue',
            name='date_modified',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
