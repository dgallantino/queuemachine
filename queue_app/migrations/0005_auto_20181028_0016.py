# Generated by Django 2.1.1 on 2018-10-28 00:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('queue_app', '0004_service_organization'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='queue',
            options={'ordering': ['date_modified']},
        ),
        migrations.AlterField(
            model_name='service',
            name='organization',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='queue_app.Organization'),
        ),
    ]
