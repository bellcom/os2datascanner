# Generated by Django 2.2.18 on 2021-06-18 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('import_services', '0002_ldapconfig_import_into'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapconfig',
            name='import_into',
            field=models.CharField(choices=[('group', 'Grupper'), ('ou', 'Organisatoriske enheder')], default='ou', max_length=32, verbose_name='import users into'),
        ),
    ]
