# Generated by Django 2.2.10 on 2020-03-19 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('os2datascanner', '0019_purge_old_engine_properties'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='sensitivity',
            field=models.IntegerField(choices=[(0, 'Grøn'), (1, 'Gul'), (2, 'Rød'), (3, 'Sort')], default=2, verbose_name='Følsomhed'),
        ),
        migrations.AlterField(
            model_name='rule',
            name='sensitivity',
            field=models.IntegerField(choices=[(0, 'Grøn'), (1, 'Gul'), (2, 'Rød'), (3, 'Sort')], default=2, verbose_name='Følsomhed'),
        ),
    ]
