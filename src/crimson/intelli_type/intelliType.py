from typing import Dict, Any, Type, Tuple, Union
from pydantic import create_model, BaseModel, ConfigDict


class IntelliType:
    """
    A base class for creating enhanced type annotations with custom structure and validation.
    """

    _BaseModel: BaseModel = None
    # For dynamic validation implemented in the future
    meta: Any = None

    def __class_getitem__(cls, args:Union[Type,Tuple[Type, ...]])->Type:
        if type(args) is tuple:
            annotation = args[0]
            cls.meta = args[1:]
        else:
            annotation = args
        _annotation = cls.get_annotation()
        if annotation == _annotation:
            return annotation
        else:
            raise TypeError(f"Expected {_annotation}, got {annotation}")

    @classmethod
    def get_annotation(cls):
        return cls.__orig_bases__[1]

    @classmethod
    def type_safe(cls, data: Any):
        return cls.get_base_model()(data=data)

    @classmethod
    def create_base_model(cls):
        if cls._BaseModel is None:
            annotation = cls.get_annotation()
            cls._BaseModel = create_model(
                f"{cls.__name__}Props",
                data=(annotation, ...),
                __config__=ConfigDict(arbitrary_types_allowed=True)
            )
        return cls._BaseModel

    @classmethod
    def get_base_model(cls) -> BaseModel:
        return cls.create_base_model()
