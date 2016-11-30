from nodeconductor.cost_tracking import CostTrackingRegister, CostTrackingStrategy, ConsumableItem

from . import models


class InstanceStrategy(CostTrackingStrategy):
    resource_class = models.Instance

    class Types(object):
        FLAVOR = 'flavor'

    @classmethod
    def get_consumable_items(cls):
        return [ConsumableItem(item_type=cls.Types.FLAVOR, key=size.backend_id) for size in models.Size.objects.all()]

    @classmethod
    def get_configuration(cls, instance):
        return {}


CostTrackingRegister.register_strategy(InstanceStrategy)
