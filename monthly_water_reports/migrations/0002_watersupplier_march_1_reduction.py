# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersupplier',
            name='march_1_reduction',
            field=models.FloatField(null=True, verbose_name=b'March 1 2016 Reduction Percent', blank=True),
        ),
    ]
