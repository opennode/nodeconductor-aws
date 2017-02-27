# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


def copy_external_ips(apps, schema_editor):
    Instance = apps.get_model('nodeconductor_aws', 'Instance')
    for instance in Instance.objects.iterator():
        instance.public_ips = instance.external_ips
        instance.save()


class Migration(migrations.Migration):

    dependencies = [
        ('nodeconductor_aws', '0002_remove_awsservice_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='instance',
            name='private_ips',
            field=jsonfield.fields.JSONField(default=[], help_text='List of private IP addresses', blank=True),
        ),
        migrations.AddField(
            model_name='instance',
            name='public_ips',
            field=jsonfield.fields.JSONField(default=[], help_text='List of public IP addresses', blank=True),
        ),
        migrations.RunPython(copy_external_ips),
        migrations.RemoveField(
            model_name='instance',
            name='external_ips',
        ),
        migrations.RemoveField(
            model_name='instance',
            name='internal_ips',
        ),
    ]
