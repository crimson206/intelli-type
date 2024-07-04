from typing import (
    get_origin,
    get_args,
    Union,
    Type,
    Any,
    _UnionGenericAlias,
    TypeVar,
)
from types import GenericAlias

# The problem that forced this implementation is simply solved by using the _annotation field instead.
# It is planned to be deprecated.


T = TypeVar("T")


class as_union:
    """
    If your type has Union, your IntelliType must look like

    class MyIntelliType(IntelliType, Tuple[as_union, int, str, ...], Generic[T])
        '''
        Descriptioin
        '''

    You don't need the setup when you typehint.

    def function(arg: MyIntelliType[Union[int, str, ...]])

    """


def replace_tuple(
    annotation: Union[Type, GenericAlias, Any]
) -> Union[Type, GenericAlias, Any]:
    origin, args = get_origin(annotation), get_args(annotation)
    if len(args) != 0:
        if str(args[0]).find("as_union") != -1:
            annotation = Union[args[1:]]
        else:
            annotation = origin[args]
    return annotation


def check_as_union(annotation: Union[Type, GenericAlias, Any]) -> bool:
    origin = get_origin(annotation)
    args = get_args(annotation)
    if len(args) > 1:
        if all([str(args[0]).find("as_union") != -1, origin is tuple]):
            return True
    return False


def replace_tuple_multi(
    annotation: Union[Type, GenericAlias, Any]
) -> Union[Type, GenericAlias, Any]:
    for _ in range(5):
        if check_as_union(annotation):
            annotation = replace_tuple(annotation)
        else:
            return annotation


class TypeNode:
    def __init__(self, type_annotation):
        type_annotation = replace_tuple_multi(type_annotation)
        self.args = []
        self.original = type_annotation

        args = get_args(type_annotation)

        if len(args) > 1:
            self.type = get_origin(type_annotation)
            if any([type_annotation is GenericAlias or _UnionGenericAlias]):
                for arg in args:
                    self.args.append(TypeNode(arg))
        else:
            self.type = type_annotation

    def __repr__(self) -> str:
        if not self.args:
            return str(self.type)
        return f"{self.type}{self.args}"


def _reconstruct_type(node: TypeNode) -> Union[Type, GenericAlias, Any]:
    if not node.args:
        return node.type

    args = tuple(_reconstruct_type(arg) for arg in node.args)
    return node.type[args]


def reconstruct_type(
    annotation: Union[Type, GenericAlias, Any]
) -> Union[Type, GenericAlias, Any]:
    type_node = TypeNode(annotation)
    annotation = _reconstruct_type(type_node)
    return annotation
