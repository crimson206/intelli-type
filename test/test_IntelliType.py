import pytest
from typing import Dict, List, Tuple, Any
from pydantic import ValidationError
from my_types import IntelliType, UploadTimesType, LatestPeriodsType, RelativeStabilityType


def test_intelli_type_get_annotation():
    assert UploadTimesType.get_annotation() == Dict[str, str]
    assert LatestPeriodsType.get_annotation() == List[Tuple[str, int]]
    assert RelativeStabilityType.get_annotation() == List[Tuple[str, float]]


def test_intelli_type_type_safe():
    valid_data = {"1.0.0": "2023-06-01T12:00:00Z"}
    result:UploadTimesType = UploadTimesType.type_safe(valid_data)
    assert result.data == valid_data

    invalid_data = {"invalid_key": 123}
    with pytest.raises(ValidationError):
        UploadTimesType.type_safe(invalid_data)


def test_intelli_type_create_base_model():
    model = UploadTimesType.create_base_model()
    assert model.__name__ == "UploadTimesTypeProps"

    valid_data = {"1.0.0": "2023-06-01T12:00:00Z"}
    instance = model(data=valid_data)
    assert instance.data == valid_data


if __name__ == "__main__":
    pytest.main()
