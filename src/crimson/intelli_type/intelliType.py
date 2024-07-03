from typing import Any, Type, Tuple, Union, TypeVar, ClassVar
from types import GenericAlias
from pydantic import BaseModel

from ._util import _create_base_model
from ._handle_union import ( # noqa : F401
    handel_as_union_def,
    handle_as_union,
    as_union,
    as_union_def,
)


T = TypeVar("T")


class IntelliType:
    """
    A base class for creating enhanced type annotations with custom structure and validation.
    """

    _BaseModel: ClassVar[Type[BaseModel]] = None
    # For dynamic validation implemented in the future
    _meta: ClassVar[Any] = None

    _annotation: Union[Type[T], Tuple[Type[T], ...]] = None

    def __class_getitem__(
        cls, annotation: Union[Type[T], Tuple[Type[T], ...]]
    ) -> Type[T]:
        annotation = handle_as_union(annotation)

        if type(annotation) is tuple:
            cls._meta = annotation[1:]
            annotation = annotation[0]
        else:
            annotation = annotation

        cls_annotation = cls.get_annotation()
        if annotation == cls_annotation:
            return annotation
        else:
            raise TypeError(f"Expected {cls_annotation}, got {annotation}")

    @classmethod
    def get_annotation(cls) -> Union[Type, GenericAlias]:
        if cls._annotation is None:
            cls._annotation = handel_as_union_def(cls.__orig_bases__[1])

        return cls._annotation

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
