# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0002_watersupplier_march_1_reduction'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='watersupplier',
            name='supplier_mwd_member',
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='supplier_active',
            field=models.BooleanField(default=True, verbose_name=b'Supplier is active'),
        ),
    ]
