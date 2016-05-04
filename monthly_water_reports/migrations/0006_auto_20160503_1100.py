# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0005_watersupplier_missed_reduction_target'),
    ]

    operations = [
        migrations.RenameField(
            model_name='watersupplier',
            old_name='missed_reduction_target',
            new_name='reached_initial_reduction_target',
        ),
    ]
