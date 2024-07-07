import pytest
from typing import TypeVar, Generic
from pydantic import BaseModel
from crimson.intelli_type import IntelliType

T = TypeVar("T")


def test_class_getitem_simple():
    class MyType(IntelliType[BaseModel], Generic[T]):
        pass

    assert MyType[BaseModel] == BaseModel
