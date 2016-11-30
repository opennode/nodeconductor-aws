import factory

from django.core.urlresolvers import reverse

from nodeconductor.structure.tests import factories as structure_factories

from .. import models


class AWSServiceFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.AWSService

    name = factory.Sequence(lambda n: 'AWS service%s' % n)
    settings = factory.SubFactory(structure_factories.ServiceSettingsFactory, type='Amazon')
    customer = factory.SubFactory(structure_factories.CustomerFactory)

    @classmethod
    def get_url(cls, service=None):
        if service is None:
            service = AWSServiceFactory()
        return 'http://testserver' + reverse('aws-detail', kwargs={'uuid': service.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('aws-list')


class AWSServiceProjectLinkFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.AWSServiceProjectLink

    service = factory.SubFactory(AWSServiceFactory)
    project = factory.SubFactory(structure_factories.ProjectFactory)


class ImageFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Image

    name = factory.Sequence(lambda n: 'image%s' % n)
    backend_id = factory.Sequence(lambda n: 'image-id%s' % n)

    @classmethod
    def get_url(cls, image=None):
        if image is None:
            image = ImageFactory()
        return 'http://testserver' + reverse('aws-image-detail', kwargs={'uuid': image.uuid})

    @classmethod
    def get_list_url(cls):
        return 'http://testserver' + reverse('aws-image-list')


class RegionFactory(factory.DjangoModelFactory):
    class Meta(object):
        model = models.Region

    name = factory.Sequence(lambda n: 'region%s' % n)
    backend_id = factory.sequence(lambda n: 'id-%s' % n)
