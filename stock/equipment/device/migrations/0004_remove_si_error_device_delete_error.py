# Generated by Django 4.2 on 2024-09-21 14:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('device', '0003_si_result_alter_location_name_alter_position_name_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='si',
            name='error_device',
        ),
        migrations.DeleteModel(
            name='Error',
        ),
    ]
