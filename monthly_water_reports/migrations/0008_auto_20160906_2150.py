# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0007_auto_20160906_2131'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watersupplier',
            name='estimated_annual_demand',
        ),
        migrations.RemoveField(
            model_name='watersupplier',
            name='estimated_annual_total_supply',
        ),
    ]
