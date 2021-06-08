# Generated by Django 2.2.18 on 2021-06-07 12:11

from django.db import migrations
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0055_pythonise_ews_validation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scanner',
            name='schedule',
            field=recurrence.fields.RecurrenceField(
                blank=True,
                max_length=1024,
                null=True,
                verbose_name='Planlagt afvikling'
            ),
        ),
    ]