from typing import Any, Type, Tuple, Union, TypeVar, ClassVar
from types import GenericAlias
from pydantic import BaseModel

from ._util import _create_base_model
from ._replace_union import reconstruct_type

T = TypeVar("T")


class IntelliType:
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

        if str(cls.__orig_bases__[1]).find("as_union") != -1:
            annoation_for_typecheck = reconstruct_type(annotation)
        else:
            annoation_for_typecheck = annotation

        if annoation_for_typecheck == cls_annotation:
            return annotation
        else:
            raise TypeError(f"Expected {cls_annotation}, got {annoation_for_typecheck}")

    @classmethod
    def get_annotation(cls) -> Union[Type, GenericAlias]:
        if cls._annotation is None:
            cls.create_annotation()
        return cls._annotation

    @classmethod
    def create_annotation(cls):
        annotation = cls.__orig_bases__[1]
        if str(annotation).find("as_union") != -1:
            cls._annotation = reconstruct_type(annotation)
        else:
            cls._annotation = annotation

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
