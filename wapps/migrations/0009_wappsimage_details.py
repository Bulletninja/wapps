# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-05 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wapps', '0008_default_page_seo_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='wappsimage',
            name='details',
            field=models.TextField(blank=True, null=True, verbose_name='Details'),
        ),
    ]
