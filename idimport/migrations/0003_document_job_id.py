# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('idimport', '0002_document_batch_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='job_id',
            field=models.CharField(default=None, max_length=12),
        ),
    ]
