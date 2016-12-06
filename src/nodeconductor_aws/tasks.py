from celery import shared_task, chain
from django.utils import timezone

from nodeconductor.core.tasks import save_error_message, transition, retry_if_false, Task, ErrorStateTransitionTask

from .models import Instance, Volume
from .backend import AWSBackendError


@shared_task(name='nodeconductor_aws.destroy')
@transition(Instance, 'begin_deleting')
@save_error_message
def destroy(instance_uuid, transition_entity=None):
    instance = transition_entity
    try:
        backend = instance.get_backend()
        backend.destroy_instance(instance)
    except:
        set_erred(instance_uuid)
        raise
    else:
        instance.delete()


@shared_task(name='nodeconductor_aws.start')
def start(instance_uuid):
    chain(
        begin_starting.s(instance_uuid),
        wait_for_instance_state.si(instance_uuid, 'RUNNING'),
    ).apply_async(
        link=set_online.si(instance_uuid),
        link_error=set_erred.si(instance_uuid))


@shared_task(name='nodeconductor_aws.stop')
def stop(instance_uuid):
    chain(
        begin_stopping.s(instance_uuid),
        wait_for_instance_state.si(instance_uuid, 'STOPPED'),
    ).apply_async(
        link=set_offline.si(instance_uuid),
        link_error=set_erred.si(instance_uuid))


@shared_task(name='nodeconductor_aws.restart')
def restart(instance_uuid):
    Instance.objects.get(uuid=instance_uuid)
    chain(
        begin_restarting.s(instance_uuid),
        wait_for_instance_state.si(instance_uuid, 'RUNNING'),
    ).apply_async(
        link=set_online.si(instance_uuid),
        link_error=set_erred.si(instance_uuid))


@shared_task(max_retries=300, default_retry_delay=3)
@retry_if_false
def wait_for_instance_state(instance_uuid, state=''):
    instance = Instance.objects.get(uuid=instance_uuid)
    try:
        backend = instance.get_backend()
        manager = backend.get_manager(instance)
        backend_instance = manager.get_node(instance.backend_id)
    except AWSBackendError:
        return False
    return backend_instance.state == backend.State.fromstring(state)


@shared_task
@transition(Instance, 'begin_starting')
@save_error_message
def begin_starting(instance_uuid, transition_entity=None):
    instance = transition_entity
    backend = instance.get_backend()
    backend.start_instance(instance)


@shared_task
@transition(Instance, 'begin_stopping')
@save_error_message
def begin_stopping(instance_uuid, transition_entity=None):
    instance = transition_entity
    backend = instance.get_backend()
    backend.stop_instance(instance)


@shared_task
@transition(Instance, 'begin_restarting')
@save_error_message
def begin_restarting(instance_uuid, transition_entity=None):
    instance = transition_entity
    backend = instance.get_backend()
    backend.reboot_instance(instance)


@shared_task
@transition(Instance, 'set_online')
def set_online(instance_uuid, transition_entity=None):
    instance = transition_entity
    instance.start_time = timezone.now()

    backend = instance.get_backend()
    manager = backend.get_manager(instance)
    backend_instance = manager.get_node(instance.backend_id)
    instance.external_ips = backend_instance.public_ips[0]

    instance.save(update_fields=['start_time', 'external_ips'])


@shared_task
@transition(Instance, 'set_offline')
def set_offline(instance_uuid, transition_entity=None):
    instance = transition_entity
    instance.start_time = None
    instance.save(update_fields=['start_time'])


@shared_task
@transition(Instance, 'set_erred')
def set_erred(instance_uuid, transition_entity=None):
    pass


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
