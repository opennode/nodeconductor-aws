from django.utils.functional import cached_property

from nodeconductor.structure.tests.fixtures import ProjectFixture

from . import factories


class AWSFixture(ProjectFixture):

    @cached_property
    def service(self):
        return factories.AWSServiceFactory(customer=self.customer)

    @cached_property
    def spl(self):
        return factories.AWSServiceProjectLinkFactory(service=self.service, project=self.project)

    @cached_property
    def region(self):
        return factories.RegionFactory()

    @cached_property
    def image(self):
        return factories.ImageFactory(region=self.region)

    @cached_property
    def size(self):
        size = factories.SizeFactory()
        size.regions.add(self.region)
        return size
