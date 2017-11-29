from __future__ import unicode_literals

from nodeconductor.core import NodeConductorExtension


class AWSExtension(NodeConductorExtension):

    @staticmethod
    def django_app():
        return 'waldur_aws'

    @staticmethod
    def rest_urls():
        from .urls import register_in
        return register_in

    @staticmethod
    def get_cleanup_executor():
        from .executors import AWSCleanupExecutor
        return AWSCleanupExecutor
