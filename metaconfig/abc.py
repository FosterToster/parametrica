from typing import Any, Callable, Type, TypeVar, Generic, Union
import typing
from functools import lru_cache

T = TypeVar('T')
       
class MetaRule(type):

    def __getitem__(class_, restrictions) -> Type['ABCRule']:
        if not isinstance(restrictions, tuple):
            restrictions = (restrictions,)
            
        class _RestrictedRule(class_):
            __restrictions__ = (*class_.__restrictions__, *restrictions)

        return _RestrictedRule


class ABCRule(metaclass=MetaRule):
    __restrictions__ = tuple()

    def __init__(self, value: Any) -> None:
        self.value = value

    @property
    def restrictions(self):
        return self.__restrictions__
    
    def try_check(self, value: Any) -> Any:
        ...

    def __call__(self, value: Any) -> Any:
        r = self.try_check(value)
        return r or value

    def __str__(self):
        return f'{self.__class__.__name__}({self.value})'

    def type_check(self, type: Type[Any]):
        for t in self.restrictions:
            if issubclass(type, t):
                break
        else:
            raise TypeError(f'Field type "{type}" does not compatible with some assigned rules')


class ABCField(Generic[T]):

    def __init__(self, default: Union[T, Callable[[], T]]):
        self.__default__ = default
        # default validation
        tmp_default = self.get_default()
        tmp_default = self.__validate_value__(self.__normalize_value__(tmp_default))
        # default ok
        self.__field_name__ = ''
        self.__label__ = ''
        self.__hint__ = ''
        self.__rule__: ABCRule = None
        self.__secret__ = False

    def __try_find_value__(self) -> T:
        raise ValueError('Not Found')

    def __get__(self, instance, class_) -> T:
        print(self.__name__, instance, class_)

        try:
            return self.__try_find_value__()
        except ValueError:
            return self.__set_value__(self.get_default())

    def __set__(self, _: T) -> T:
        raise TypeError(f'Field value can not be assigned. Use Metaconfig.update() method instead.')

    def __normalize_value__(self, value: Any) -> T:
        if not isinstance(value, self.__type__):
            return self.__type__(value)
        else:
            return value

    def __validate_value__(self, value: T) -> T:
        #TODO
        return value

    def __set_value__(self, value: Any) -> T:
        value = self.__normalize_value__(value)
        value = self.__validate_value__(value)

        #TODO write storage

        return value
        

    def get_default(self) -> T:
        if callable(self.__default__):
            return self.__default__()
        else:
            return self.__default__

    def __class_getitem__(self, args):
        class _TypedField(self):
            __type__ = args

        return _TypedField

    def __clone__(self):
        new_field = self.__class__(self.__default__)
        new_field.__field_name__ = self.__field_name__
        new_field.__label__ = self.__label__
        new_field.__hint__ = self.__hint__
        new_field.__rule__ = self.__rule__
        new_field.__secret__ = self.__secret__

        return new_field



