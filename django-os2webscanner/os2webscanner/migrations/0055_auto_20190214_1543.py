# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2019-02-14 14:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('os2webscanner', '0054_auto_20190213_1626'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scan',
            name='do_cpr_ignore_irrelevant',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='do_cpr_modulus11',
        ),
        migrations.RemoveField(
            model_name='scan',
            name='do_cpr_scan',
        ),
    ]
