from typing import Any, Type, Tuple, Union, TypeVar
from types import GenericAlias
from pydantic import BaseModel
from ._util import _create_base_model

T = TypeVar("T")


class IntelliType:
    """
    A base class for creating enhanced type annotations with custom structure and validation.

    ex)
        class MyIntelliType(IntelliType[List[int, str]], Generic[T]):
            '''
            Description for the type.
            '''

        def function(important_arg:MyIntelliType[List[int, str]]):
            pass

        - If you hover on MyIntelliType, you can read the description.
    """

    _BaseModel: Type[BaseModel] = None
    # For dynamic validation implemented in the future
    _meta: Tuple[Any] = None

    _annotation: Union[Type[T], Tuple[Type[T], ...]] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._annotation = cls._annotation_tmp
        cls._meta = cls._meta_tmp
        print(f"A new subclass of ParentClass has been created: {cls.__name__}")

    def __class_getitem__(
        cls, annotation: Union[Type[T], Tuple[Type[T], ...]]
    ) -> Type[T]:

        annotation, meta = _handle_meta(annotation)

        if cls.__name__ == "IntelliType":
            cls._annotation_tmp = annotation
            cls._meta_tmp = meta
            return IntelliType
        else:
            cls._meta = meta
            if cls._annotation != annotation:
                raise TypeError(f"Type mismatch: expected {cls._annotation}, but got {annotation}")
            else:
                return annotation

    @classmethod
    def get_annotation(cls) -> Union[Type, GenericAlias]:
        return cls._annotation

    @classmethod
    def get_meta(cls) -> Tuple[Any]:
        return cls._meta

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


AnyType = TypeVar("AnyType")


def _handle_meta(data: Union[Tuple, AnyType]) -> Tuple[AnyType, Any]:
    if type(data) is tuple:
        annotation = data[0]
        meta = data[1:]
    else:
        annotation = data
        meta = None

    return annotation, meta
