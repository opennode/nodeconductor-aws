import six

from rest_framework import decorators, exceptions, viewsets

from nodeconductor.core.views import StateExecutorViewSet
from nodeconductor.core.exceptions import IncorrectStateException
from nodeconductor.structure import views as structure_views

from . import filters, models, serializers, executors


class AmazonServiceViewSet(structure_views.BaseServiceViewSet):
    queryset = models.AWSService.objects.all()
    serializer_class = serializers.ServiceSerializer
    import_serializer_class = serializers.InstanceImportSerializer

    def get_import_context(self):
        return {'resource_type': self.request.query_params.get('resource_type')}

    def get_serializer_class(self):
        from nodeconductor.structure import SupportedServices

        if self.request.method == 'POST':
            resource_type = self.request.data.get('type')
            if resource_type == SupportedServices.get_name_for_model(models.Instance):
                return serializers.InstanceImportSerializer
            elif resource_type == SupportedServices.get_name_for_model(models.Volume):
                return serializers.VolumeImportSerializer
        return super(AmazonServiceViewSet, self).get_serializer_class()


class AmazonServiceProjectLinkViewSet(structure_views.BaseServiceProjectLinkViewSet):
    queryset = models.AWSServiceProjectLink.objects.all()
    serializer_class = serializers.ServiceProjectLinkSerializer


class RegionViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Region.objects.all()
    serializer_class = serializers.RegionSerializer
    lookup_field = 'uuid'


class ImageViewSet(structure_views.BaseServicePropertyViewSet):
    queryset = models.Image.objects.all()
    serializer_class = serializers.ImageSerializer
    filter_class = filters.ImageFilter
    lookup_field = 'uuid'


class SizeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.Size.objects.all()
    serializer_class = serializers.SizeSerializer
    filter_class = filters.SizeFilter
    lookup_field = 'uuid'


class InstanceViewSet(structure_views.BaseResourceViewSet):
    queryset = models.Instance.objects.all()
    serializer_class = serializers.InstanceSerializer

    serializers = {
        'resize': serializers.InstanceResizeSerializer
    }

    def get_serializer_class(self):
        serializer = self.serializers.get(self.action)
        return serializer or super(InstanceViewSet, self).get_serializer_class()

    def perform_provision(self, serializer):
        instance = serializer.save()
        volume = instance.volume_set.first()

        executors.InstanceCreateExecutor.execute(
            instance,
            image=serializer.validated_data.get('image'),
            size=serializer.validated_data.get('size'),
            ssh_key=serializer.validated_data.get('ssh_public_key'),
            volume=volume
        )

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=models.Instance.States.OFFLINE)
    def resize(self, request, instance, uuid=None):
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        new_size = serializer.validated_data.get('size')
        executors.InstanceResizeExecutor().execute(instance, size=new_size)


class VolumeViewSet(six.with_metaclass(structure_views.ResourceViewMetaclass,
                                       structure_views.ResourceViewMixin,
                                       StateExecutorViewSet)):
    queryset = models.Volume.objects.all()
    serializer_class = serializers.VolumeSerializer
    create_executor = executors.VolumeCreateExecutor
    delete_executor = executors.VolumeDeleteExecutor

    serializers = {
        'attach': serializers.VolumeAttachSerializer
    }

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=models.Volume.States.OK)
    def detach(self, request, volume, uuid=None):
        if not volume.instance:
            raise exceptions.ValidationError('Volume is already detached.')
        elif volume.instance.state != models.Instance.States.OFFLINE:
            raise IncorrectStateException('Volume instance must be in offline state.')

        executors.VolumeDetachExecutor.execute(volume)

    @decorators.detail_route(methods=['post'])
    @structure_views.safe_operation(valid_state=models.Volume.States.OK)
    def attach(self, request, volume, uuid=None):
        serializer = self.get_serializer(volume, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        executors.VolumeAttachExecutor.execute(volume)

    def get_serializer_class(self):
        serializer = self.serializers.get(self.action)
        return serializer or super(VolumeViewSet, self).get_serializer_class()
