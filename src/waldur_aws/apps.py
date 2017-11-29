from django.apps import AppConfig


class AWSConfig(AppConfig):
    name = 'waldur_aws'
    verbose_name = "Waldur AWS EC2"
    service_name = 'Amazon'
    is_public_service = True

    def ready(self):
        from nodeconductor.structure import SupportedServices

        from .backend import AWSBackend
        SupportedServices.register_backend(AWSBackend)
