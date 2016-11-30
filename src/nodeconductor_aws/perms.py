from nodeconductor.core.permissions import StaffPermissionLogic
from nodeconductor.structure import perms as structure_perms


PERMISSION_LOGICS = (
    ('nodeconductor_aws.AWSService', structure_perms.service_permission_logic),
    ('nodeconductor_aws.AWSServiceProjectLink', structure_perms.service_project_link_permission_logic),
    ('nodeconductor_aws.Instance', structure_perms.resource_permission_logic),
    ('nodeconductor_aws.Volume', structure_perms.resource_permission_logic),
    ('nodeconductor_aws.Image', StaffPermissionLogic(any_permission=True)),
    ('nodeconductor_aws.Region', StaffPermissionLogic(any_permission=True)),
)
