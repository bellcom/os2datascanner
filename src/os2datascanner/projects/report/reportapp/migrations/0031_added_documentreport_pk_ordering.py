# Generated by Django 3.2.4 on 2021-08-10 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner_report', '0030_changing_documentreport_created_timestamp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='documentreport',
            options={'ordering': ['-sensitivity', '-probability', 'pk'], 'verbose_name_plural': 'document reports'},
        ),
    ]
