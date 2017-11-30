# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-11-29 12:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_fsm
import model_utils.fields
import waldur_core.core.fields
import waldur_core.core.models
import waldur_core.core.validators
import waldur_core.logging.loggers
import taggit.managers


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        ('structure', '0052_customer_subnets'),
    ]

    operations = [
        migrations.CreateModel(
            name='AWSService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('available_for_all', models.BooleanField(default=False, help_text='Service will be automatically added to all customers projects if it is available for all')),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Customer', verbose_name='organization')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'AWS provider',
                'verbose_name_plural': 'AWS providers',
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='AWSServiceProjectLink',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.Project')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='waldur_aws.AWSService')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'AWS provider project link',
                'verbose_name_plural': 'AWS provider project links',
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(waldur_core.core.models.BackendModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Instance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='description')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('runtime_state', models.CharField(blank=True, max_length=150, verbose_name='runtime state')),
                ('state', django_fsm.FSMIntegerField(choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')], default=5)),
                ('backend_id', models.CharField(blank=True, max_length=255)),
                ('cores', models.PositiveSmallIntegerField(default=0, help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(default=0, help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(default=0, help_text='Disk size in MiB')),
                ('min_ram', models.PositiveIntegerField(default=0, help_text='Minimum memory size in MiB')),
                ('min_disk', models.PositiveIntegerField(default=0, help_text='Minimum disk size in MiB')),
                ('image_name', models.CharField(blank=True, max_length=150)),
                ('key_name', models.CharField(blank=True, max_length=50)),
                ('key_fingerprint', models.CharField(blank=True, max_length=47)),
                ('user_data', models.TextField(blank=True, help_text='Additional data that will be added to instance on provisioning')),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('public_ips', waldur_core.core.fields.JSONField(blank=True, default=[], help_text='List of public IP addresses')),
                ('private_ips', waldur_core.core.fields.JSONField(blank=True, default=[], help_text='List of private IP addresses')),
                ('size_backend_id', models.CharField(blank=True, max_length=150)),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.core.models.BackendModelMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(max_length=255, unique=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(waldur_core.core.models.BackendModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('backend_id', models.CharField(max_length=255, unique=True)),
                ('cores', models.PositiveSmallIntegerField(help_text='Number of cores in a VM')),
                ('ram', models.PositiveIntegerField(help_text='Memory size in MiB')),
                ('disk', models.PositiveIntegerField(help_text='Disk size in MiB')),
                ('price', models.DecimalField(decimal_places=5, default=0, max_digits=11, verbose_name='Hourly price rate')),
                ('regions', models.ManyToManyField(to='waldur_aws.Region')),
            ],
            options={
                'ordering': ['cores', 'ram'],
            },
            bases=(waldur_core.core.models.BackendModelMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('description', models.CharField(blank=True, max_length=500, verbose_name='description')),
                ('name', models.CharField(max_length=150, validators=[waldur_core.core.validators.validate_name], verbose_name='name')),
                ('uuid', waldur_core.core.fields.UUIDField()),
                ('error_message', models.TextField(blank=True)),
                ('runtime_state', models.CharField(blank=True, max_length=150, verbose_name='runtime state')),
                ('state', django_fsm.FSMIntegerField(choices=[(5, 'Creation Scheduled'), (6, 'Creating'), (1, 'Update Scheduled'), (2, 'Updating'), (7, 'Deletion Scheduled'), (8, 'Deleting'), (3, 'OK'), (4, 'Erred')], default=5)),
                ('backend_id', models.CharField(blank=True, max_length=255)),
                ('size', models.PositiveIntegerField(help_text='Size of volume in gigabytes')),
                ('volume_type', models.CharField(choices=[('gp2', 'General Purpose SSD'), ('io1', 'Provisioned IOPS SSD'), ('standard', 'Magnetic volumes')], max_length=8)),
                ('device', models.CharField(blank=True, max_length=128, null=True)),
                ('instance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='waldur_aws.Instance')),
                ('region', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='waldur_aws.Region')),
                ('service_project_link', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='volumes', to='waldur_aws.AWSServiceProjectLink')),
                ('tags', taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags')),
            ],
            options={
                'abstract': False,
            },
            bases=(waldur_core.core.models.DescendantMixin, waldur_core.core.models.BackendModelMixin, waldur_core.logging.loggers.LoggableMixin, models.Model),
        ),
        migrations.AddField(
            model_name='instance',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='waldur_aws.Region'),
        ),
        migrations.AddField(
            model_name='instance',
            name='service_project_link',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='waldur_aws.AWSServiceProjectLink'),
        ),
        migrations.AddField(
            model_name='instance',
            name='tags',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='image',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='waldur_aws.Region'),
        ),
        migrations.AddField(
            model_name='awsservice',
            name='projects',
            field=models.ManyToManyField(related_name='aws_services', through='waldur_aws.AWSServiceProjectLink', to='structure.Project'),
        ),
        migrations.AddField(
            model_name='awsservice',
            name='settings',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='structure.ServiceSettings'),
        ),
        migrations.AlterUniqueTogether(
            name='awsserviceprojectlink',
            unique_together=set([('service', 'project')]),
        ),
        migrations.AlterUniqueTogether(
            name='awsservice',
            unique_together=set([('customer', 'settings')]),
        ),
    ]
