# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0008_auto_20160906_2150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='waterincentive',
            name='supplier_name',
        ),
        migrations.RemoveField(
            model_name='waterrestriction',
            name='supplier_name',
        ),
        migrations.DeleteModel(
            name='WaterIncentive',
        ),
        migrations.DeleteModel(
            name='WaterRestriction',
        ),
    ]
