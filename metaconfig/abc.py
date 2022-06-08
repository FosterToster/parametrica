import enum
from typing import Any, Callable, Dict, Type, TypeVar, Generic, Union, overload
from .io import ConfigIOInterface

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


class Dataset:
    def __init__(self, data: dict):
        self.__data__ = data

    @property
    def data(self):
        return self.__data__

    def get_item_by_path(self, path):
        path = [x.strip() for x in path.split('.') if x.strip()] 
        node = self.data
        for name in path:
            try:
                idx = int(name)
            except ValueError:
                if name not in node.keys():
                    raise AttributeError(f'Value by requested path is not found')
                node = node.get(name)
            else:
                node = node[idx]

        return node


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

        self.__value__ = None
        self.__name__ = ''
        self.__label__ = ''
        self.__hint__ = ''
        self.__rule__: ABCRule = None
        self.__secret__ = False

        self.__get_default__()

    def __set_value__(self, value, instance: '_FieldRW') -> 'ABCField':
        try:
            new_field = self.__clone__()
            if self.__is_primitive_type__():
                new_field.__value__ = new_field.__normalize_value__(value)
            elif self.__is_iterable_type__():
                if not hasattr(value, '__iter__'):
                    value = [value,]
                result = []
                for current in self.__get__(instance, instance.__class__):
                    try:
                        new = value.pop(0)
                        result.append(current.__set_value__(new))
                    except IndexError:
                        result.append(current)

                for new in value:
                    result.append(self.__generic_type__()().__set_value__(new))

                new_field.__value__ = result
            else: # Fieldset
                new_field.__value__ = self.__get__(instance, instance.__class__).__set_value__(value)
        except ValueError as e:
            raise ValueError(f'{self.__name__} -> {e}') from e
        return new_field

    def __export_data__(self, instance: '_FieldRW'):
        if self.__is_primitive_type__():
            return self.__get__(instance, instance.__class__)
        elif self.__is_iterable_type__():
            return tuple(x.__export_data__(instance) for x in self.__get__(instance, instance.__class__))
        else:
            return self.__get__(instance, instance.__class__).__export_data__(instance)
        

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
        new_field = self.__clone__()
        new_field.__default__ = value
        new_field.__get_default__()
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
                raise ValueError(f'Type {arg} can`t be used as Field type')

        
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

        return new_field


class MetaFieldset(type):

    def __new__(class_, name, bases, dict):
        metafields = list()

        # inherit metafield names
        for base in bases:
            if hasattr(base, '__metafields__'):
                for field_name in base.__metafields__:
                    if not (field_name in metafields):
                        metafields.append(field_name)
        
        # find new metafields
        for key, value in dict.items():
            if isinstance(value, ABCField):
                if not (key in metafields):
                    metafields.append(key)
                value.__name__ = key
    
        fieldset = super().__new__(class_, name, bases, dict)
        fieldset.__metafields__ = metafields
        return fieldset

class _FieldRW:
    
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
                raise TypeError(f'{class_.__name__} does not have field named {name}')

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


class ABCFieldset(ABCField, _FieldRW, metaclass=MetaFieldset):
    
    def __init__(self,**default_fields: Dict[str, Any]):
        defaults = {
            # **default_keyset,
            **default_fields
        }
        for key, value in defaults.items():
            field: ABCField = self.__get_field__(key)
            self.__set_field__(key, field.__new_default__(value))
        

    def __get_default__(self) -> dict:
        defaults = {}
        for field_name in self.__metafields__:
            defaults[field_name] = self.__get_field__(field_name).__get_default__()
            if isinstance(defaults[field_name], ABCField):
                defaults[field_name] = defaults[field_name].get_default()
        return defaults

    def __set_value__(self, dataset: dict) -> 'ABCFieldset':
        new_fieldset = self.__clone__()
        for field_name, value in dataset.items():
            if not field_name in self.__metafields__:
                continue
            field: ABCField = new_fieldset.__get_field__(field_name)
            # try:
            new_fieldset.__set_field__(field_name, field.__set_value__(value, new_fieldset))
            # except ValueError as e:
            #     raise ValueError(f'{new_fieldset.__class__.__name__} -> {e}') from e
        
        return self

    def __export_data__(self, instance: '_FieldRW'):
        return dict((field_name, self.__get_field__(field_name).__export_data__(self)) for field_name in self.__metafields__)        

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

    def __clone__(self, new_default: Any = {}):
        new_fieldset = self.__class__(**new_default)
        new_fieldset.__dict__ = self.__dict__
        return new_fieldset

    

class ABCMetaconfig(_FieldRW, metaclass=MetaFieldset):
    def _initialize(self, io_class: ConfigIOInterface):
        self.__name__ = ''
        self.__io_class__ = io_class


    def __dataset__(self) -> dict:
        return dict((field_name, self.__get_field__(field_name).__export_data__(self)) for field_name in self.__metafields__)

    def __update__(self, dataset: dict):
        for field_name, value in dataset.items():
            if not field_name in self.__metafields__:
                continue
            field: ABCField = self.__get_field__(field_name)
            try:
                self.__set_field__(field_name, field.__set_value__(value, self))
            except ValueError as e:
                raise ValueError(f'{self.__class__.__name__} -> {e}') from e


