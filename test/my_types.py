from typing import Generic, TypeVar, Dict, List, Tuple
from crimson.intelli_type import IntelliType

T = TypeVar("T")


class UploadTimesType(IntelliType, Dict[str, str], Generic[T]):
    """
    Type Description:
        - version: A string representing the version number.
        - upload_time: A string representing the upload time in ISO format.

    Structure: Dict[str, str]
        { version: upload_time }

    Example:
        {
            "1.0.0": "2023-06-01T12:00:00Z",
            "1.0.1": "2023-06-02T12:00:00Z"
        }
    """


class LatestPeriodsType(IntelliType, List[Tuple[str, int]], Generic[T]):
    """
    Type Description:
        - version: A string representing the version number.
        - period: An integer representing the period in days.

    Structure: List[Tuple[str, int]]
        [(version, period), ...]

    Example:
        [
            ("1.0.1", 1),
            ("1.0.0", 2)
        ]
    """


class RelativeStabilityType(IntelliType, List[Tuple[str, float]], Generic[T]):
    """
    Type Description:
        - version: A string representing the version number.
        - zscore: A float representing the z-score of the version's stability.

    Structure: List[Tuple[str, float]]
        [(version, zscore), ...]

    Example:
        [
            ("1.0.1", 0.5),
            ("1.0.0", -1.2)
        ]
    """
