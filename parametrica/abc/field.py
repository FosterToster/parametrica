import enum
from typing import Any, Callable, Dict, Type, TypeVar, Generic, Union, overload

from  .rule import ABCRule

T = TypeVar('T')
       

class ABCField(Generic[T]):

    @overload
    def __init__(self, default: Union[T, Callable[[], T]]):
        pass

    @overload
    def __init__(self, **default_fields: Dict[str, Any]):
        pass
       
    def __init__(self, default: Union[T, Callable[[], T]] = None, **default_fields: Dict[str, Any]) -> None:
        if hasattr(self, '__default__'): # prevent double initialization
            return

        self.__default__ = self.__resolve_default__(default, **default_fields)

        self.__value__ = None
        self.__name__ = ''
        self.__label__ = ''
        self.__hint__ = ''
        self.__rule__: ABCRule = None
        self.__secret__ = False
        self.__password__ = False

        self.__get_default__()
    
    def __resolve_default__(self, default: Union[T, Callable[[], T]] = None, **default_fields: Dict[str, Any]) -> Any:
        if default is None:
            if self.__is_iterable_type__():
                if self.__is_primitive_type__():
                    return tuple()
                else:
                    return (self.__generic_type__()(**default_fields),)
            else:
                if self.__is_primitive_type__():
                    raise ValueError(f'Fields of primitive types must have an explicit default value')
                else:
                    return self.__generic_type__()(**default_fields)
        else:
            if self.__is_iterable_type__():
                if hasattr(default, '__iter__'):
                    return default
                else:
                    return (default,)
            else:
                return default

    def __set_value__(self, value, instance: '_FieldRW') -> 'ABCField':
        if self.__secret__:
            self.__secret__ = False
        try:
            new_field = self.__clone__()
            if self.__is_primitive_type__():
                new_field.__value__ = new_field.__normalize_value__(value)
            elif self.__is_iterable_type__():
                if not hasattr(value, '__iter__') or isinstance(value, dict):
                    value = [value,]
                result = []
                for current in self.__get__(instance, instance.__class__):
                    try:
                        new = value.pop(0)
                        result.append(current.__set_value__(new))
                    except IndexError:
                        pass

                for new in value:
                    result.append(self.__generic_type__()().__set_value__(new))

                new_field.__value__ = result
            else: # Fieldset
                new_field.__value__ = self.__get__(instance, instance.__class__).__set_value__(value)
        except ValueError as e:
            raise ValueError(f'{self.__name__} -> {e}') from e
        return new_field

    def __export_data__(self, instance: '_FieldRW', *, export_secret: bool = False):
        if self.__is_primitive_type__():
            val = self.__get__(instance, instance.__class__)
            if isinstance(val, enum.Enum):
                return val.value
            else:
                return val
        elif self.__is_iterable_type__():
            return tuple(x.__export_data__(instance, export_secret=export_secret) for x in self.__get__(instance, instance.__class__))
        else:
            return self.__get__(instance, instance.__class__).__export_data__(instance, export_secret=export_secret)
        

    def __try_find_value__(self, from_: 'ABCFieldset' = None) -> T:
        if (from_ or self).__value__ is None:
            raise AttributeError(f'Value is not assigned')
        else:
            return (from_ or self).__value__

    def __get__(self, instance:'_FieldRW', _) -> T:
        try:
            return self.__try_find_value__(instance.__get_field__(self.__name__))
        except AttributeError:
            return self.__get_default__(instance.__get_field__(self.__name__))

    def __set__(self, _: T) -> T:
        raise TypeError(f'Field value can not be assigned. Use [Metaconfig].update() method instead.')

    def __is_iterable_type__(self, type_ = None) -> bool:
        return str(type_ or self.__type__).startswith( ('typing.List', 'typing.Tuple', 'typing.Iterable') )

    def __generic_type__(self) -> Type[T]:
        if self.__is_iterable_type__():
            return self.__type__.__args__[0]
        else:
            return self.__type__

    def __is_primitive_type__(self, type_ = None) -> bool:
        typ = type_ or self.__generic_type__()
        return (typ in (int, str, float, bool)) or (issubclass(typ, enum.Enum))
        # return self.__generic_type__() in 

    def __ensure_type__(self, value: Any) -> T:
        required_type = self.__generic_type__()
        
        # try:
        if type(value) != required_type:
            return required_type(value)
        else:
            return value
        # except ValueError as e:
        #     raise ValueError(f'{self.__name__} -> {e}') from e

    def __normalize_value__(self, value: Any) -> T:
        if self.__is_iterable_type__():
            if not hasattr(value, '__iter__'):
                value = (value,)

            return tuple(self.__validate_value__( self.__ensure_type__( item ) ) for item in value)
            
        return self.__validate_value__( self.__ensure_type__( value ) )

    def __validate_value__(self, value: T) -> T:
        # try:
            if self.__rule__:
                self.__rule__(value)
            return value
        # except ValueError as e:
        #     raise ValueError(f'{self.__name__}: {e}') from e
        
    def __new_default__(self, value: Union[T, Callable[[], T]]):
        new_field = self.__clone__(value)
        return new_field

    def __get_default__(self, from_: 'ABCFieldset' = None) -> T:
        field = (from_ or self)
        
        if callable(field.__default__):
            value = field.__default__()
        else:
            value = field.__default__

        return field.__normalize_value__(value)

    @classmethod
    def __check_generic_type__(class_, arg):
        if class_.__is_iterable_type__(class_, arg):
            return class_.__check_generic_type__(arg.__args__[0])
        
        if not class_.__is_primitive_type__(class_, arg):
            if not issubclass(arg, ABCFieldset):
                raise TypeError(f'Type {arg} can`t be used as Field type')

        
    def __class_getitem__(class_, arg):
        if not str(arg).startswith('~'):
            class_.__check_generic_type__(arg)

        class _TypedField(class_):
            __type__ = arg

        return _TypedField

    def __clone__(self, new_default: Any = None):
        new_field = self.__class__(new_default or self.__default__)
        new_field.__name__ = self.__name__
        new_field.__label__ = self.__label__
        new_field.__hint__ = self.__hint__
        new_field.__rule__ = self.__rule__
        new_field.__secret__ = self.__secret__
        new_field.__password__ = self.__password__

        return new_field

    def __metadata__(self, instance: '_FieldRW'):
        if self.__is_primitive_type__():
            return {
                'is_primitive': True,
                'is_iterable': self.__is_iterable_type__(),
                'type': self.__generic_type__().__name__,
                'default': self.__get_default__(instance.__get_field__(self.__name__)),
                'name': self.__name__,
                'label': self.__label__,
                'hint': self.__hint__,
                'rule': str(self.__rule__) if self.__rule__ else None,
                'secret': self.__secret__,
                'password': self.__password__
            }
        else:
            return {
                'is_primitive': False,
                'is_iterable': self.__is_iterable_type__(),
                'type': self.__get__(instance, instance.__class__).__metadata__(instance),
                # 'default': self.__get_default__(instance).__metadata__(instance),
                'name': self.__name__,
                'label': self.__label__,
                'hint': self.__hint__,
                'secret': self.__secret__,
                'password': self.__password__
            }


from .fieldset import ABCFieldset, _FieldRW