# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-04-11 11:38
from __future__ import unicode_literals

from django.db import migrations, models
import recurrence.fields


class Migration(migrations.Migration):

    dependencies = [
        ('os2webscanner', '0004_auto_20180103_1504'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scanner',
            name='do_collect_cookies',
            field=models.BooleanField(default=False, verbose_name='Indsaml cookies'),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='do_cpr_ignore_irrelevant',
            field=models.BooleanField(default=True, verbose_name='Tjek om CPR-nummer indeholder ugyldige fødselsdatoer'),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='do_cpr_modulus11',
            field=models.BooleanField(default=True, verbose_name='Tjek om CPR-nummer opfylder modulus-11'),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='do_cpr_scan',
            field=models.BooleanField(default=True, verbose_name='Scan efter CPR-numre'),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='do_external_link_check',
            field=models.BooleanField(default=False, verbose_name='Tjek om eksterne links virker'),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='do_last_modified_check',
            field=models.BooleanField(default=True, verbose_name='Scan kun fil eller html-side hvis der er blevet foretaget ændringer siden sidste scan.'),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='do_last_modified_check_head_request',
            field=models.BooleanField(default=True, verbose_name='Forsøg at spare båndbredde (via HTTP Head request).'),
        ),
        migrations.AlterField(
            model_name='scanner',
            name='schedule',
            field=recurrence.fields.RecurrenceField(max_length=1024, null=True, verbose_name='Planlagt afvikling'),
        ),
    ]
