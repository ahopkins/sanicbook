from __future__ import annotations

from dataclasses import dataclass, field, fields
from datetime import date, datetime
from enum import Enum
from inspect import getmembers
from typing import Any, List, Optional
from uuid import UUID

import ujson


class BaseEnum(str, Enum):
    def _generate_next_value_(name, *_):
        return name.lower()


@dataclass
class MetaState:
    exclude: List[str] = field(default_factory=list)
    include_null: bool = field(default=True)


@dataclass
class Config:
    pk_field: str = field(default="")


def pkdataclass(decorated_class, *args, **kwargs):
    def wrapper(cls):
        orig = getattr(cls, "__init__")
        derived = dataclass(cls, *args, **kwargs)
        setattr(derived, "__default_init__", derived.__init__)
        setattr(derived, "__init__", orig)
        return derived

    built = wrapper(decorated_class)
    built.__name__ = decorated_class.__name__
    built.__doc__ = decorated_class.__doc__
    return built


class BaseModelMeta(type):
    __config__: Config

    def __new__(meta_class, name, bases, namespace, **kwargs):
        meta_args = {}
        if "Meta" in namespace:
            meta_args = {
                k: v
                for k, v in namespace["Meta"].__dict__.items()
                if not k.startswith("__")
            }
        cls = super().__new__(meta_class, name, bases, namespace, **kwargs)
        cls.__config__ = Config(**meta_args)
        return pkdataclass(cls)


class BaseModel(metaclass=BaseModelMeta):
    __state__: MetaState = field(repr=False)

    def __init__(self, *args, **kwargs) -> None:
        meta_state = MetaState()
        meta_state.exclude.extend([self.__config__.pk_field, "__state__"])
        kwargs["__state__"] = meta_state
        if self.__config__.pk_field and self.__config__.pk_field not in kwargs:
            kwargs[self.__config__.pk_field] = None
        self.__default_init__(*args, **kwargs)  # type: ignore

    def __json__(self):
        return ujson.dumps(self.to_dict(clean=True))

    @property
    def __config__(self) -> Config:
        return self.__class__.__config__  # type: ignore

    def to_dict(
        self,
        *,
        clean: bool = False,
        include_null: Optional[bool] = None,
        cascade: bool = True,
    ):
        if include_null is not None:
            self.set_state("include_null", include_null, cascade)
        output = {}
        for fld in fields(self):
            value = getattr(self, fld.name)
            if isinstance(value, BaseModel):
                value = value.to_dict(clean=clean)
            if clean:
                value = self._clean(value)
            if fld.name not in self.__state__.exclude and (
                self.__state__.include_null or value is not None
            ):
                output[fld.name] = value
        return output

    def set_state(self, key: str, value: Any, cascade: bool = False) -> None:
        setattr(self.__state__, key, value)
        if cascade:
            for _, member in getmembers(self, BaseModel._predicate):
                member.set_state(key, value, cascade)

    @classmethod
    def _predicate(cls, obj: Any) -> bool:
        return isinstance(obj, BaseModel)

    @staticmethod
    def _clean(value):
        if isinstance(value, (date, datetime)):
            return value.isoformat()
        elif isinstance(value, UUID):
            return str(value)
        return value
