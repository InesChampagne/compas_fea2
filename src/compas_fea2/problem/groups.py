from typing import TYPE_CHECKING
from typing import Iterable
from typing import Set

from compas_fea2.model.groups import _Group
from compas_fea2.problem.fields import ForceField
from compas_fea2.problem.fields import GravityLoadField
from compas_fea2.problem.loads import VectorLoad
from compas_fea2.problem.fields import DisplacementField

from compas.tolerance import TOL

# Type-checking imports to avoid circular dependencies at runtime
if TYPE_CHECKING:
    from compas_fea2.problem.displacements import GeneralDisplacement
    from compas_fea2.problem.fields import DisplacementField
    from compas_fea2.problem.fields import ForceField
    from compas_fea2.problem.loads import _Load


class LoadsGroup(_Group["_Load"]):
    """Base class for groups of loads."""

    def __init__(self, members: Iterable["_Load"] | "_Load", **kwargs) -> None:
        from compas_fea2.problem.loads import _Load

        if isinstance(members, _Load):
            members = [members]
        super().__init__(members=members, member_class=_Load, **kwargs)

    @property
    def loads(self) -> Set["_Load"]:
        return self._members


class DisplacementsGroup(_Group["GeneralDisplacement"]):
    """Base class for groups of displacements."""

    def __init__(self, members: Iterable["GeneralDisplacement"] | "GeneralDisplacement", **kwargs) -> None:
        from compas_fea2.problem.displacements import GeneralDisplacement

        if isinstance(members, "GeneralDisplacement"):
            members = [members]
        super().__init__(members=members, member_class=GeneralDisplacement, **kwargs)

    @property
    def displacements(self) -> Set["GeneralDisplacement"]:
        return self._members


class LoadsFieldGroup(_Group["DisplacementField | ForceField"]):
    """Base class for groups of loads that can be applied to a field."""

    def __init__(self, members: "Iterable[DisplacementField | ForceField] | DisplacementField | ForceField", **kwargs) -> None:
        from compas_fea2.problem.fields import _BaseLoadField

        if not isinstance(members, Iterable):
            members = [members]
        super().__init__(members=members, member_class=_BaseLoadField, **kwargs)

    @property
    def fields(self) -> "Iterable[DisplacementField | ForceField]":
        return self._members
    

    @property
    def node_loads_all_fields(self) -> _Group["DisplacementField | ForceField"]:
        dof = ['x', 'y', 'z', 'xx', 'yy', 'zz']
        node_loads_all_fields = {}

        for field in self.fields:
            if isinstance(field, GravityLoadField) or isinstance(field, DisplacementField):
                continue

            for node, load in field.node_load:

                if node in node_loads_all_fields:
                    for component in dof:
                        a = getattr(load, component, None)
                        b = getattr(node_loads_all_fields[node], component, None)
                        if a:
                            if b:
                                    setattr(node_loads_all_fields[node], component, a+b)
                            else :
                                setattr(node_loads_all_fields[node], component, a)
                    if node_loads_all_fields[node].force_vector.length <1e-6 :
                        del node_loads_all_fields[node]
                        continue

                else:
                    node_loads_all_fields[node] = VectorLoad(**load.components)


        return node_loads_all_fields