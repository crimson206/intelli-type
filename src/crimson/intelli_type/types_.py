from .intelliType import IntelliType
from typing import Type, Any, TypeVar, Tuple, Generic
from types import GenericAlias

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


class Annotation_(IntelliType, Tuple[as_union, Type, GenericAlias, Any], Generic[T]):
    """
    Annotation

    """
