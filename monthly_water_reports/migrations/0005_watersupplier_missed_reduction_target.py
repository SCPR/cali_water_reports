# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0004_auto_20160502_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersupplier',
            name='missed_reduction_target',
            field=models.BooleanField(default=False, verbose_name=b'Supplier met the conservation target'),
        ),
    ]
