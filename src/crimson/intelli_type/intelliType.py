from typing import Any, Type, Tuple, Union, TypeVar, ClassVar, Generic
from types import GenericAlias
from pydantic import BaseModel

from ._util import _create_base_model

T = TypeVar("T")


class IntelliType():
    """
    A base class for creating enhanced type annotations with custom structure and validation.

    ex)
        class MyIntelliType(IntelliType, List[int, str], Generic[T]):
            '''
            Description for the type.
            '''

        def function(important_arg:MyIntelliType[List[int, str]]):
            pass

        - If you hover on MyIntelliType, you can read the description.
    """

    _BaseModel: ClassVar[Type[BaseModel]] = None
    # For dynamic validation implemented in the future
    _meta: ClassVar[Any] = None

    _annotation: Union[Type[T], Tuple[Type[T], ...]] = None

    def __class_getitem__(
        cls, annotation: Union[Type[T], Tuple[Type[T], ...]]
    ) -> Type[T]:
        """
        It allows IntelliType to mimic the enclosed type.

        ex1) MyIntelliType[List[int, str]] returns List[int, str] by this function.

        ex2) MyIntelliType[List[int, str], 'Any Meta']
            You can use it with additional metadata. Only the first component is the annotation, and the rest components are metadata.
            Currently, it doesn't have additional features.
        """
        if type(annotation) is tuple:
            cls._meta = annotation[1:]
            annotation = annotation[0]
        else:
            annotation = annotation

        cls_annotation = cls.get_annotation()

        annoation_for_typecheck = annotation

        if annoation_for_typecheck == cls_annotation:
            return annotation
        else:
            raise TypeError(f"Expected {cls_annotation}, got {annoation_for_typecheck}")

    @classmethod
    def get_annotation(cls) -> Union[Type, GenericAlias]:
        if cls._annotation is None:
            cls.create_annoataion()
        return cls._annotation

    @classmethod
    def create_annoataion(cls) -> Union[Type, GenericAlias]:
        if str(cls.__orig_bases__[1]) == str(Generic[T]):
            cls._annotation = cls.__orig_bases__[2]
        else:
            cls._annotation = cls.__orig_bases__[1]
        return cls._annotation

    # I am not sure if we need them. They can be deprecated.

    @classmethod
    def get_base_model(cls) -> Type[BaseModel]:
        return cls.create_base_model()

    @classmethod
    def type_safe(cls: Type[T], data: Any) -> T:
        return cls.get_base_model()(data=data).data

    @classmethod
    def create_base_model(cls) -> Type[BaseModel]:
        if cls._BaseModel is None:
            annotation = cls.get_annotation()
            cls._BaseModel = _create_base_model(annotation, cls.__name__)

        return cls._BaseModel
