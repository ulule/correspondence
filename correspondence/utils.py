from enum import Enum as BaseEnum
from enum import EnumType
from typing import Type, TypeVar

T = TypeVar("T")


class Enum(BaseEnum):
    @classmethod
    def choices(cls: Type[T]) -> dict[str, T]:
        return dict((item.name.lower(), item.value) for item in cls)  # type: ignore

    @classmethod
    def to_payload(cls) -> EnumType:
        keys = cls.choices()
        # see https://github.com/python/mypy/issues/6037
        return BaseEnum(cls.__name__, zip(keys, keys))  # type: ignore
