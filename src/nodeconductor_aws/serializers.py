from django.db import transaction
from rest_framework import serializers

from nodeconductor.core import serializers as core_serializers
from nodeconductor.structure import serializers as structure_serializers

from . import models
from .backend import AWSBackendError


class ServiceSerializer(core_serializers.ExtraFieldOptionsMixin,
                        structure_serializers.BaseServiceSerializer):

    SERVICE_ACCOUNT_FIELDS = {
        'username': '',
        'token': '',
    }

    SERVICE_ACCOUNT_EXTRA_FIELDS = {
        'images_regex': ''
    }

    class Meta(structure_serializers.BaseServiceSerializer.Meta):
        model = models.AWSService
        view_name = 'aws-detail'
        extra_field_options = {
            'username': {
                'label': 'Access key ID',
                'required': True
            },
            'token': {
                'label': 'Secret access key',
                'required': True
            },
            'images_regex': {
                'help_text': 'Regular expression to limit images list'
            }
        }


class RegionSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Region
        fields = ('url', 'uuid', 'name')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'aws-region-detail'}
        }


class ImageSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Image
        fields = ('url', 'uuid', 'name', 'region')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'aws-image-detail'}
        }

    region = RegionSerializer(read_only=True)


class SizeSerializer(structure_serializers.BasePropertySerializer):

    class Meta(object):
        model = models.Size
        fields = ('url', 'uuid', 'name', 'cores', 'ram', 'disk', 'regions', 'description')
        extra_kwargs = {
            'url': {'lookup_field': 'uuid', 'view_name': 'aws-size-detail'}
        }

    # AWS expose a more technical backend_id as a name. AWS's short codes are more popular
    name = serializers.ReadOnlyField(source='backend_id')
    description = serializers.ReadOnlyField(source='name')
    regions = RegionSerializer(many=True, read_only=True)


class ServiceProjectLinkSerializer(structure_serializers.BaseServiceProjectLinkSerializer):

    class Meta(structure_serializers.BaseServiceProjectLinkSerializer.Meta):
        model = models.AWSServiceProjectLink
        view_name = 'aws-spl-detail'
        extra_kwargs = {
            'service': {'lookup_field': 'uuid', 'view_name': 'aws-detail'},
        }


class AWSImportSerializerMixin(object):
    def get_fields(self):
        from nodeconductor.structure import SupportedServices
        fields = super(AWSImportSerializerMixin, self).get_fields()
        resources = SupportedServices.get_service_resources(models.AWSService)
        choices = [SupportedServices.get_name_for_model(resource) for resource in resources]
        fields['type'] = serializers.ChoiceField(choices=choices, write_only=True)
        return fields


class InstanceSerializer(structure_serializers.VirtualMachineSerializer):
    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='aws-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='aws-spl-detail',
        queryset=models.AWSServiceProjectLink.objects.all())

    region = serializers.HyperlinkedRelatedField(
        view_name='aws-region-detail',
        lookup_field='uuid',
        queryset=models.Region.objects.all(),
        write_only=True)

    image = serializers.HyperlinkedRelatedField(
        view_name='aws-image-detail',
        lookup_field='uuid',
        queryset=models.Image.objects.all(),
        write_only=True)

    size = serializers.HyperlinkedRelatedField(
        view_name='aws-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all(),
        write_only=True)

    class Meta(structure_serializers.VirtualMachineSerializer.Meta):
        model = models.Instance
        view_name = 'aws-instance-detail'
        fields = structure_serializers.VirtualMachineSerializer.Meta.fields + (
            'region', 'image', 'size'
        )
        protected_fields = structure_serializers.VirtualMachineSerializer.Meta.protected_fields + (
            'region', 'image', 'size'
        )

    def validate(self, attrs):
        region = attrs['region']
        image = attrs['image']
        size = attrs['size']

        if image.region != region:
            raise serializers.ValidationError("Image is missing in region %s" % region.name)

        if not size.regions.filter(pk=region.pk).exists():
            raise serializers.ValidationError("Size is missing in region %s" % region.name)

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        size = validated_data.get('size')
        ssh_key = validated_data.get('ssh_public_key')

        validated_data['ram'] = size.ram
        validated_data['cores'] = size.cores
        validated_data['disk'] = size.disk

        if ssh_key is not None:
            validated_data['key_name'] = ssh_key.name
            validated_data['key_fingerprint'] = ssh_key.fingerprint

        instance = super(InstanceSerializer, self).create(validated_data)
        volume = {
            'name': ('temp-%s' % instance.name)[:150],
            'state': models.Volume.States.CREATION_SCHEDULED,
            'instance': instance,
            'service_project_link': instance.service_project_link,
            'region': instance.region,
            # Size will be received from the backend
            'size': 0
        }
        models.Volume.objects.create(**volume)

        return instance


class InstanceImportSerializer(AWSImportSerializerMixin,
                               structure_serializers.BaseResourceImportSerializer):
    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.Instance
        view_name = 'aws-instance-detail'

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            region, instance = backend.find_instance(validated_data['backend_id'])
        except AWSBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find instance with ID %s" % validated_data['backend_id']})

        validated_data['name'] = instance['name']
        validated_data['external_ips'] = instance['external_ips']
        validated_data['cores'] = instance['cores']
        validated_data['ram'] = instance['ram']
        validated_data['disk'] = instance['disk']
        validated_data['created'] = instance['created']
        validated_data['state'] = instance['state']
        validated_data['region'] = region
        validated_data.pop('type')

        return super(InstanceImportSerializer, self).create(validated_data)


class InstanceResizeSerializer(structure_serializers.PermissionFieldFilteringMixin,
                               serializers.Serializer):
    size = serializers.HyperlinkedRelatedField(
        view_name='aws-size-detail',
        lookup_field='uuid',
        queryset=models.Size.objects.all(),
    )

    def get_fields(self):
        fields = super(InstanceResizeSerializer, self).get_fields()
        if self.instance:
            fields['size'].query_params = {
                'region_uuid': self.instance.region.uuid
            }
        return fields

    def get_filtered_field_names(self):
        return ('size',)

    def validate(self, attrs):
        size = attrs['size']

        if not size.regions.filter(uuid=self.instance.region.uuid).exists():
            raise serializers.ValidationError("New size is not within the same region.")

        if (size.ram, size.disk, size.cores) == (self.instance.ram, self.instance.disk, self.instance.cores):
            raise serializers.ValidationError("New size is the same as current.")

        if size.disk < self.instance.disk:
            raise serializers.ValidationError("New disk size should be greater than the previous value")

        return attrs

    def update(self, instance, validated_data):
        size = validated_data.get('size')

        instance.ram = size.ram
        instance.cores = size.cores
        instance.disk = size.disk
        instance.save(update_fields=['ram', 'cores', 'disk'])
        return instance


class VolumeSerializer(structure_serializers.BaseResourceSerializer):
    service = serializers.HyperlinkedRelatedField(
        source='service_project_link.service',
        view_name='aws-detail',
        read_only=True,
        lookup_field='uuid')

    service_project_link = serializers.HyperlinkedRelatedField(
        view_name='aws-spl-detail',
        queryset=models.AWSServiceProjectLink.objects.all())

    region = serializers.HyperlinkedRelatedField(
        view_name='aws-region-detail',
        lookup_field='uuid',
        queryset=models.Region.objects.all(),
        write_only=True)

    class Meta(structure_serializers.BaseResourceSerializer.Meta):
        model = models.Volume
        view_name = 'aws-volume-detail'

        protected_fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'size', 'region', 'volume_type'
        )
        read_only_fields = structure_serializers.BaseResourceSerializer.Meta.read_only_fields + (
            'device', 'instance', 'runtime_state'
        )
        fields = structure_serializers.BaseResourceSerializer.Meta.fields + (
            'size', 'region', 'volume_type', 'device', 'instance', 'runtime_state'
        )
        extra_kwargs = {
            'url': {'lookup_field': 'uuid'},
            'instance': {'lookup_field': 'uuid', 'view_name': 'aws-instance-detail'}
        }


class VolumeImportSerializer(AWSImportSerializerMixin,
                             structure_serializers.BaseResourceImportSerializer):
    class Meta(structure_serializers.BaseResourceImportSerializer.Meta):
        model = models.Volume
        view_name = 'aws-volume-detail'

    def create(self, validated_data):
        backend = self.context['service'].get_backend()
        try:
            region, volume = backend.find_volume(validated_data['backend_id'])
        except AWSBackendError:
            raise serializers.ValidationError(
                {'backend_id': "Can't find volume with ID %s" % validated_data['backend_id']})

        instance_id = volume['instance_id']
        if instance_id:
            try:
                instance = models.Instance.objects.get(backend_id=instance_id)
            except models.Instance.DoesNotExist:
                raise serializers.ValidationError(
                    "You must import instance with ID %s first" % instance_id)
            else:
                validated_data['instance'] = instance

        validated_data['name'] = volume['name']
        validated_data['size'] = volume['size']
        validated_data['created'] = volume['created']
        validated_data['runtime_state'] = volume['runtime_state']
        validated_data['state'] = models.Volume.States.OK
        validated_data['device'] = volume['device']
        validated_data['volume_type'] = volume['volume_type']
        validated_data['region'] = region
        validated_data.pop('type')

        return super(VolumeImportSerializer, self).create(validated_data)


class VolumeAttachSerializer(structure_serializers.PermissionFieldFilteringMixin,
                             serializers.Serializer):
    instance = serializers.HyperlinkedRelatedField(
        view_name='aws-instance-detail',
        lookup_field='uuid',
        queryset=models.Instance.objects.all(),
    )
    device = serializers.CharField(
        max_length=128,
        help_text='The device name for attachment. For example, use /dev/sd[f-p] for Linux instances.'
    )

    def get_fields(self):
        fields = super(VolumeAttachSerializer, self).get_fields()
        if self.instance:
            fields['instance'].query_params = {
                'region_uuid': self.instance.region.uuid
            }
        return fields

    def get_filtered_field_names(self):
        return ('instance',)

    def validate(self, attrs):
        volume = self.instance
        instance = attrs['instance']

        if volume.instance:
            raise serializers.ValidationError("Volume is already attached to instance.")

        if volume.region != instance.region:
            raise serializers.ValidationError("Instance is not within the same region.")

        if instance.state != models.Instance.States.OFFLINE:
            raise serializers.ValidationError("Instance must be in offline state.")

        return attrs

    def update(self, volume, validated_data):
        volume.instance = validated_data.get('instance')
        volume.device = validated_data.get('device')
        volume.save(update_fields=['instance', 'device'])

        return volume
