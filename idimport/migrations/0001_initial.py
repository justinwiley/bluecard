# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import idimport.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.FileField(upload_to=idimport.models.PathAndRename(b'/imports'))),
                ('status', models.CharField(default=b'imported', max_length=30)),
                ('value1', models.CharField(default=None, max_length=250)),
                ('value2', models.CharField(default=None, max_length=250)),
                ('current', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('customer', models.ForeignKey(to='idimport.Customer')),
            ],
        ),
    ]
