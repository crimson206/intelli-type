from typing import Any, Type, Tuple, Union, TypeVar, Generic
from types import GenericAlias
from pydantic import BaseModel
from ._util import _create_base_model

T = TypeVar("T")


class IntelliType(Generic[T]):
    """

    ## Tip:
    Copy and paste below to use IntelliType.

    ---
    ``` python
        from typing import Generic, TypeVar
        T = TypeVar('T')
    ```
    ---


    ## Description:

    A base class for creating enhanced type annotations with custom structure and validation.

    ex)

    ---
    ``` python
        class MyIntelliType(IntelliType[List[int, str]], Generic[T]):
            '''
            Description for the type.
            '''
        def function(important_arg:MyIntelliType[List[int, str]]):
            pass
    ```
    ---

    If you hover on MyIntelliType, you can read the description.
    """

    _BaseModel: Type[BaseModel] = None
    # For dynamic validation implemented in the future
    meta: Tuple[Any] = None

    annotation: Type[T] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if hasattr(cls, '_annotation_tmp'):
            cls.annotation = cls._annotation_tmp
            cls.meta = cls._meta_tmp   

    def __class_getitem__(
        cls, annotation: Union[Type[T], Tuple[Type[T], ...]]
    ) -> Type[T]:

        annotation, meta = _handle_meta(annotation)

        if cls.__name__ == "IntelliType":
            cls._annotation_tmp = annotation
            cls._meta_tmp = meta
            return IntelliType
        elif cls.annotation is None:
            cls.create_annotation()

        else:
            cls.meta = meta
            if cls.annotation != annotation:
                raise TypeError(
                    f"Type mismatch: expected {cls.annotation}, but got {annotation}"
                )
            else:
                return annotation

    @classmethod
    def get_annotation(cls) -> Union[Type, GenericAlias]:
        if cls.annotation is None:
            cls.create_annotation()
        return cls.annotation

    @classmethod
    def create_annotation(cls):
        if len(cls.__orig_bases__) > 1:
            annotation = cls.__orig_bases__[1]
        else:
            return
        cls.annotation = annotation

    @classmethod
    def get_meta(cls) -> Tuple[Any]:
        return cls.meta

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
