# Generated by Django 2.1.1 on 2018-11-02 15:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('queue_app', '0006_queue_print_datetime'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='queue',
            options={'ordering': ['date_created']},
        ),
    ]
