# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('monthly_water_reports', '0003_auto_20160502_1158'),
    ]

    operations = [
        migrations.AddField(
            model_name='watersupplier',
            name='category_definition',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Compliance Priority Category Definition', blank=True),
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='compliance_priority',
            field=models.CharField(max_length=255, null=True, verbose_name=b'Compliance Priority', blank=True),
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='cumulative_percent_saved',
            field=models.FloatField(null=True, verbose_name=b'Cumulative Percent Saved Compared to 2013', blank=True),
        ),
        migrations.AddField(
            model_name='watersupplier',
            name='missed_reduction_target_by',
            field=models.FloatField(null=True, verbose_name=b'Missed Conservation Standard By Percentage Points', blank=True),
        ),
    ]
