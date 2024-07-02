from typing import Any, Type, Tuple, Union, TypeVar, ClassVar
from types import GenericAlias
from pydantic import create_model, BaseModel, ConfigDict

T = TypeVar("T")


class IntelliType:
    """
    A base class for creating enhanced type annotations with custom structure and validation.
    """

    _BaseModel: ClassVar[Type[BaseModel]] = None
    # For dynamic validation implemented in the future
    _meta: ClassVar[Any] = None

    def __class_getitem__(cls, args: Union[Type[T], Tuple[Type[T], ...]]) -> Type[T]:
        """
        Implements the functionality for using the class with square brackets.

        This method allows for specifying the type and optional metadata when using the class.
        For example: MyType[List[int], r"metadata"]. # r"" is to escape a warning.

        Args:
            args: Either a single type or a tuple containing a type and metadata.

        Returns:
            The specified type if it matches the class's annotation.

        Raises:
            TypeError: If the specified type doesn't match the class's annotation.
        """
        if type(args) is tuple:
            annotation = args[0]
            cls._meta = args[1:]
        else:
            annotation = args
        _annotation = cls.get_annotation()
        if annotation == _annotation:
            return annotation
        else:
            raise TypeError(f"Expected {_annotation}, got {annotation}")

    @classmethod
    def get_annotation(cls) -> Union[Type, GenericAlias]:
        """
        Retrieves the type annotation associated with this class.

        Returns:
            The type annotation specified when defining the class.
        """
        return cls.__orig_bases__[1]

    @classmethod
    def type_safe(cls: Type[T], data: Any) -> T:
        """
        Performs runtime type checking and validation on the provided data.

        This method creates a Pydantic model instance to validate the data
        against the class's type annotation.

        Args:
            data: The data to be type-checked and validated.

        Returns:
            The validated data, with the type T.
        """
        return cls.get_base_model()(data=data).data

    @classmethod
    def create_base_model(cls) -> Type[BaseModel]:
        """
        Creates a Pydantic BaseModel for this class if it doesn't exist.

        This method is used internally to generate a Pydantic model
        based on the class's type annotation for validation purposes.

        Returns:
            A Pydantic BaseModel subclass.
        """
        if cls._BaseModel is None:
            annotation = cls.get_annotation()
            cls._BaseModel = create_model(
                f"{cls.__name__}Props",
                data=(annotation, ...),
                __config__=ConfigDict(arbitrary_types_allowed=True),
            )
        return cls._BaseModel

    @classmethod
    def get_base_model(cls) -> Type[BaseModel]:
        """
        Retrieves the Pydantic BaseModel associated with this class.

        If the BaseModel doesn't exist, it creates one using create_base_model().

        Returns:
            A Pydantic BaseModel subclass.
        """
        return cls.create_base_model()
