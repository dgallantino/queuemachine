# Generated by Django 2.1 on 2018-08-29 11:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queue_app', '0006_auto_20180829_1129'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='queue',
            options={'ordering': ['date_created']},
        ),
    ]
