import enum
from typing import Any, Callable, Dict, Iterable, List, Sequence, Tuple, Type, TypeVar, Generic, Union, overload

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


class FieldsetDataProxy:
    root_data = None
    names_path = ''


class ABCField(Generic[T]):

    @overload
    def __init__(self, default: Union[T, Callable[[], T]]):
        ...

    @overload
    def __init__(self, **default_fields: Dict[str, Any]):
        ...

    def __resolve_default__(self, default: Union[T, Callable[[], T]] = None, **default_fields: Dict[str, Any]) -> Any:
        if default is None:
            if self.__is_iterable_type__():
                if self.__is_primitive_type__():
                    return tuple()
                else:
                    return (self.__generic_type__()(**default_fields),)
            else:
                if self.__is_primitive_type__():
                    raise ValueError(f'Fields of primitive types must have an explicid default value')
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

        
    def __init__(self, default: Union[T, Callable[[], T]] = None, **default_fields: Dict[str, Any]) -> None:
        self.__default__ = self.__resolve_default__(default, **default_fields)

        self.__name__ = ''
        self.__label__ = ''
        self.__hint__ = ''
        self.__rule__: ABCRule = None
        self.__secret__ = False

        self.__get_default__()


    def __try_find_value__(self, parent: 'ABCFieldset') -> T:
        raise ValueError(f'Type "{parent.__name__}" does not have metafield named "{self.__name__}"')

    def __get__(self, instance, class_) -> T:
        try:
            return self.__try_find_value__(class_)
        except ValueError:
            return self.__get_default__(instance)

    def __set__(self, _: T) -> T:
        raise TypeError(f'Field value can not be assigned. Use [Metaconfig].update() method instead.')

    def __is_iterable_type__(self) -> bool:
        return str(self.__type__).startswith( ('typing.List', 'typing.Tuple', 'typing.Iterable') )

    def __generic_type__(self) -> Type[T]:
        if self.__is_iterable_type__():
            return self.__type__.__args__[0]
        else:
            return self.__type__

    def __is_primitive_type__(self) -> bool:
        return self.__generic_type__() in (int, str, float, bool, enum.Enum)

    def __ensure_type__(self, value: Any) -> T:
        required_type = self.__generic_type__()
        
        if type(value) != required_type:
            return required_type(value)
        else:
            return value

    def __normalize_value__(self, value: Any) -> T:
        if self.__is_iterable_type__():
            if not hasattr(value, '__iter__'):
                value = (value,)

            return tuple(self.__validate_value__( self.__ensure_type__( item ) ) for item in value)
            
        # if issubclass(self.__type__, ABCFieldset):
        #     if isinstance(value, self.__type__):
        #         return value
        #     else:
        #         return self.__default__.__normalize_value__(value)
        

        return self.__validate_value__( self.__ensure_type__( value ) )

    def __validate_value__(self, value: T) -> T:
        if self.__rule__:
            self.__rule__(value)
        return value
        
    def __new_default__(self, value: Union[T, Callable[[], T]]):
        new_field = self.__clone__()
        new_field.__default__ = value
        new_field.__get_default__()
        return new_field

    def __get_default__(self, from_: 'ABCFieldset' = None) -> T:
        if from_:
            field = from_.__dict__.get(self.__name__)
            if field is None:
                field = self
        else:
            field = self

        if callable(field.__default__):
            value = field.__default__()
        else:
            value = field.__default__

        return field.__normalize_value__(value)

        
    def __class_getitem__(class_, args):
        class _TypedField(class_):
            __type__ = args

        return _TypedField

    def __clone__(self, new_default: Any = None):
        new_field = self.__class__(new_default or self.__default__)
        new_field.__name__ = self.__name__
        new_field.__label__ = self.__label__
        new_field.__hint__ = self.__hint__
        new_field.__rule__ = self.__rule__
        new_field.__secret__ = self.__secret__

        return new_field


class MetaFieldset(type):

    def __new__(class_, name, bases, dict):
        metafields = list()
        for key, value in dict.items():
            if isinstance(value, ABCField):
                metafields.append(key)
                value.__name__ = key
    
        fieldset = super().__new__(class_, name, bases, dict)
        fieldset.__metafields__ = metafields
        return fieldset


class ABCFieldset(ABCField[dict], metaclass=MetaFieldset):
    
    def __init__(self, **default_fields: Dict[str, Any]):
        for key, value in default_fields.items():
            field: ABCField = self.__get_field__(key)
            self.__set_field__(key, field.__new_default__(value))
        

    def __get_default__(self) -> dict:
        defaults = {}
        for field_name in self.__metafields__:
            defaults[field_name] = self.__get_field__(field_name).__get_default__()
            if isinstance(defaults[field_name], ABCField):
                defaults[field_name] = defaults[field_name].get_default()
        return defaults

    def __set_field__(self, name, field: ABCField):
        self.__dict__[name] = field

    @classmethod
    def __class_get_field__(class_, name) -> ABCField:
        field = class_.__dict__.get(name)
        if field is None:
            for superclass in class_.__bases__:
                if issubclass(superclass, ABCFieldset):
                    try:
                        field = superclass.__class_get_field__(name)
                    except TypeError:
                        continue
                    else:
                        break
            else:
                raise TypeError(f'{self.__class__.__name__} does not have field named {name}')

        return field

    def __get_field__(self, name: str) -> ABCField:
        field = self.__dict__.get(name)
        if field is None:
            try:
                field = self.__class_get_field__(name)
            except TypeError:
                raise TypeError(f'{self.__class__.__name__} does not have field named {name}')                
        
        if not isinstance(field, ABCField):
            raise TypeError(f'{self.__class__.__name__}\'s field {name} is not instance of Field')
        else:
            return field

    def __normalize_value__(self, dataset: dict) -> dict:
        if isinstance(dataset, self.__class__):
            return dataset.__get_default__()

        if not isinstance(dataset, dict):
            raise ValueError(f'Required <dict> as value for {self.__class__.__name__}')
        
        return self.__validate_value__(dataset)

    def __validate_value__(self, dataset: dict) -> dict:
        resultset = {}
        for key, value in dataset.items():
            try:
                field: ABCField = self.__get_field__(key)
                resultset[key] = field.__normalize_value__(value)
            except TypeError:
                continue

        return resultset
    

class ABCMetaconfig(FieldsetDataProxy, metaclass=MetaFieldset):
    def __init__(self, io_class = None):
        self.__io_class__ = io_class or 1 # TODO
        self.__default__ = None
        self.__type__ = None
        self.__name__ = self.__class__.__name__
        self.__label__ = ''
        self.__hint__ = ''
        self.__rule__: ABCRule = None
        self.__secret__ = False

    @classmethod
    def haskey(class_, key: str):
        return key in class_.__metafields__

    def get_default(self) -> dict:
        defaults = {}
        for field_name in self.__metafields__:
            defaults[field_name] = self.__class__.__dict__[field_name].get_default()
            if isinstance(defaults[field_name], ABCField):
                defaults[field_name] = defaults[field_name].get_default()
        return defaults
        # return [self.__class__.__dict__[field].get_default() for field in self.__metafields__]
        # return dict((field_name, self.__class__.__dict__[field_name].get_default()) for field_name in self.__metafields__)