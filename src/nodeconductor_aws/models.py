from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible, force_text
from libcloud.compute.drivers.ec2 import REGION_DETAILS

from nodeconductor.core.models import RuntimeStateMixin
from nodeconductor.quotas.fields import CounterQuotaField
from nodeconductor.quotas.models import QuotaModelMixin
from nodeconductor.structure import models as structure_models
from nodeconductor.structure.utils import get_coordinates_by_ip


class AWSService(structure_models.Service):
    projects = models.ManyToManyField(
        structure_models.Project, related_name='aws_services', through='AWSServiceProjectLink')

    class Meta(structure_models.Service.Meta):
        verbose_name = 'AWS service'
        verbose_name_plural = 'AWS services'

    class Quotas(QuotaModelMixin.Quotas):
        instance_count = CounterQuotaField(
            target_models=lambda: [Instance],
            path_to_scope='service_project_link.service'
        )

        volume_count = CounterQuotaField(
            target_models=lambda: [Volume],
            path_to_scope='service_project_link.service'
        )

    @classmethod
    def get_url_name(cls):
        return 'aws'


class AWSServiceProjectLink(structure_models.ServiceProjectLink):
    service = models.ForeignKey(AWSService)

    class Meta(structure_models.ServiceProjectLink.Meta):
        verbose_name = 'AWS service project link'
        verbose_name_plural = 'AWS service project links'

    @classmethod
    def get_url_name(cls):
        return 'aws-spl'


class Region(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['name']

    @classmethod
    def get_url_name(cls):
        return 'aws-region'


@python_2_unicode_compatible
class Image(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['name']

    region = models.ForeignKey(Region)

    def __str__(self):
        return '{0} | {1}'.format(self.name, self.region.name)

    @classmethod
    def get_url_name(cls):
        return 'aws-image'


class Size(structure_models.GeneralServiceProperty):
    class Meta:
        ordering = ['cores', 'ram']

    regions = models.ManyToManyField(Region)
    cores = models.PositiveSmallIntegerField(help_text='Number of cores in a VM')
    ram = models.PositiveIntegerField(help_text='Memory size in MiB')
    disk = models.PositiveIntegerField(help_text='Disk size in MiB')
    price = models.DecimalField('Hourly price rate', default=0, max_digits=11, decimal_places=5)

    @classmethod
    def get_url_name(cls):
        return 'aws-size'


class Instance(structure_models.VirtualMachineMixin, structure_models.Resource, RuntimeStateMixin):
    service_project_link = models.ForeignKey(
        AWSServiceProjectLink, related_name='instances', on_delete=models.PROTECT)

    region = models.ForeignKey(Region)

    def detect_coordinates(self):
        if self.external_ips:
            return get_coordinates_by_ip(self.external_ips)
        region = self.region.backend_id
        endpoint = REGION_DETAILS[region]['endpoint']
        return get_coordinates_by_ip(endpoint)

    # XXX: For compatibility with new-style state.
    @property
    def human_readable_state(self):
        return force_text(dict(self.States.CHOICES)[self.state])

    @classmethod
    def get_url_name(cls):
        return 'aws-instance'


class Volume(RuntimeStateMixin, structure_models.NewResource):
    service_project_link = models.ForeignKey(
        AWSServiceProjectLink, related_name='volumes', on_delete=models.PROTECT)

    VOLUME_TYPES = (
        ('gp2', 'General Purpose SSD'),
        ('io1', 'Provisioned IOPS SSD'),
        ('standard', 'Magnetic volumes')
    )
    size = models.PositiveIntegerField(help_text='Size of volume in gigabytes')
    region = models.ForeignKey(Region)
    volume_type = models.CharField(max_length=8, choices=VOLUME_TYPES)
    device = models.CharField(max_length=128, blank=True, null=True)
    instance = models.ForeignKey(Instance, blank=True, null=True)

    @classmethod
    def get_url_name(cls):
        return 'aws-volume'
