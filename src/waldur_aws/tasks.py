from nodeconductor.core.tasks import Task, ErrorStateTransitionTask

from .models import Volume


class RuntimeStateException(Exception):
    pass


class PollRuntimeStateTask(Task):
    max_retries = 300
    default_retry_delay = 5

    def get_backend(self, instance):
        return instance.get_backend()

    def execute(self, instance, backend_pull_method, success_state, erred_state):
        backend = self.get_backend(instance)
        getattr(backend, backend_pull_method)(instance)
        instance.refresh_from_db()
        if instance.runtime_state not in (success_state, erred_state):
            self.retry()
        elif instance.runtime_state == erred_state:
            raise RuntimeStateException(
                'Instance %s (PK: %s) runtime state become erred: %s' % (instance, instance.pk, erred_state))


class PollBackendCheckTask(Task):
    max_retries = 60
    default_retry_delay = 5

    @classmethod
    def get_description(cls, instance, backend_check_method, *args, **kwargs):
        return 'Check instance "%s" with method "%s"' % (instance, backend_check_method)

    def get_backend(self, instance):
        return instance.get_backend()

    def execute(self, instance, backend_check_method):
        # backend_check_method should return True if object does not exist at backend
        backend = self.get_backend(instance)
        if not getattr(backend, backend_check_method)(instance):
            self.retry()
        return instance


class SetInstanceErredTask(ErrorStateTransitionTask):
    """ Mark instance as erred and delete resources that were not created. """

    def execute(self, instance):
        super(SetInstanceErredTask, self).execute(instance)

        # delete volume if it were not created on backend,
        # mark as erred if creation was started, but not ended,
        volume = instance.volume_set.first()
        if volume.state == Volume.States.CREATION_SCHEDULED:
            volume.delete()
        elif volume.state == Volume.States.OK:
            pass
        else:
            volume.set_erred()
            volume.save(update_fields=['state'])
