# Generated by Django 2.1.1 on 2018-11-05 23:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('queue_app', '0010_auto_20181104_0036'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=12, null=True),
        ),
    ]