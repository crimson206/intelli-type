import pytest
from typing import List, Dict, TypeVar, Generic, Union, Tuple
from pydantic import BaseModel
from crimson.intelli_type import IntelliType, as_union

T = TypeVar("T")


class TestIntelliType:
    def test_class_getitem_simple(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        assert MyType[List[int]] == List[int]

    def test_class_getitem_with_union(self):
        class MyType(IntelliType, Tuple[as_union, List[int], str], Generic[T]):
            pass

        assert MyType[Union[List[int], str]] == Union[List[int], str]

    def test_class_getitem_with_deep_annotation(self):
        class MyType(IntelliType, Tuple[as_union, Tuple[as_union, int, Dict[int, str]]], Generic[T]):
            pass

        assert MyType[Union[Union[int, Dict[int, str]]]] == Union[Union[int, Dict[int, str]]]

    def test_class_getitem_complex(self):
        class NonGeneralType:
            pass

        class MyType(IntelliType, Dict[str, NonGeneralType], Generic[T]):
            pass

        assert MyType[Dict[str, NonGeneralType]] == Dict[str, NonGeneralType]

    def test_class_getitem_with_meta(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        MyType[List[int], r"meta_data"]
        assert MyType._meta == (r"meta_data",)

    def test_class_getitem_type_mismatch(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        with pytest.raises(TypeError):
            MyType[Dict[str, int]]

    def test_get_annotation(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        assert MyType.get_annotation() == List[int]

    def test_type_safe_valid(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        result = MyType.type_safe([1, 2, 3])
        assert result == [1, 2, 3]

    def test_type_safe_invalid(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        with pytest.raises(ValueError):  # pydantic raises ValueError for invalid types
            MyType.type_safe(["a", "b", "c"])

    def test_get_base_model(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        base_model = MyType.get_base_model()
        assert issubclass(base_model, BaseModel)
        assert base_model.__name__ == "MyTypeProps"

    def test_create_base_model_caching(self):
        class MyType(IntelliType, List[int], Generic[T]):
            pass

        model1 = MyType.create_base_model()
        model2 = MyType.create_base_model()
        assert model1 is model2  # 동일한 인스턴스를 반환하는지 확인


if __name__ == "__main__":
    pytest.main()
