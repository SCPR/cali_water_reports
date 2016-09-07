# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0006_auto_20160503_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersupplier',
            name='estimated_annual_demand',
            field=models.IntegerField(null=True, verbose_name=b'estimated_annual_demand', blank=True),
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='estimated_annual_total_supply',
            field=models.IntegerField(null=True, verbose_name=b'estimated_annual_total_supply', blank=True),
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='stress_test_conservation_standard',
            field=models.FloatField(null=True, verbose_name=b'stress_test_conservation_standard', blank=True),
        ),
    ]
