from nodeconductor.core.filters import UUIDFilter
from nodeconductor.structure import filters as structure_filters

from . import models


class ImageFilter(structure_filters.BaseServicePropertyFilter):

    class Meta():
        model = models.Image
        fields = structure_filters.BaseServicePropertyFilter.Meta.fields + ('region',)

    region = UUIDFilter(name='region__uuid')


class SizeFilter(structure_filters.BaseServicePropertyFilter):

    class Meta():
        model = models.Size
        fields = structure_filters.BaseServicePropertyFilter.Meta.fields + ('region',)

    region = UUIDFilter(name='regions__uuid')
