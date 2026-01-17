from ocp_tessellate import OcpGroup
from ocp_tessellate.convert import tessellate_group
from ocp_tessellate.convert import to_ocpgroup
from ocp_tessellate.utils import numpy_to_buffer_json

from .ocp_data_types import OcpData
from .ocp_data_types import OcpPayload


def convert(*cad_objs, names=None) -> OcpPayload:
    part_group, instances = to_ocpgroup(
        *cad_objs,
        names=names,
    )
    if len(part_group.objects) == 1 and isinstance(part_group.objects[0], OcpGroup):
        loc = part_group.loc
        part_group = part_group.objects[0]
        part_group.loc = loc * part_group.loc
    instances, shapes, mapping = tessellate_group(
        group=part_group,
        instances=instances,
    )

    data = numpy_to_buffer_json(
        dict(instances=instances, shapes=shapes),
    )
    return OcpPayload(
        data=OcpData.model_validate(data),
        type="data",
        count=part_group.count_shapes(),
    )
