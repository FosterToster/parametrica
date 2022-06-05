from typing import Any, Callable, Dict, Iterable, List, Tuple, Type, TypeVar, Generic, Union

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

    def __init__(self, default: Union[T, Callable[[], T]] = None):
        if default is None: 
            if issubclass(self.__type__, ABCFieldset):
                default = self.__type__()
            else:
                raise ValueError(f'Field of type {self.__type__} requires default value')

        self.__default__ = default

        self.__name__ = ''
        self.__label__ = ''
        self.__hint__ = ''
        self.__rule__: ABCRule = None
        self.__secret__ = False

        self.get_default()

    def __try_find_value__(self, parent: 'ABCFieldset') -> T:
        if issubclass(self.__type__, ABCFieldset):
            class _DataProxy(self.__type__):
                __data__ = parent.__data__.get(self.__name__)

            return  _DataProxy()

    def __get__(self, instance, class_) -> T:
        try:
            return self.__try_find_value__(instance)
        except ValueError:
            return self.get_default()

    def __set__(self, _: T) -> T:
        raise TypeError(f'Field value can not be assigned. Use Metaconfig.update() method instead.')

    def __normalize_value__(self, value: Any) -> T:
        if issubclass(self.__type__, ABCFieldset):
            if isinstance(value, self.__type__):
                return value
            else:
                return self.__default__.__normalize_value__(value)

        if not isinstance(value, self.__type__):
            value =  self.__type__(value)

        return self.__validate_value__(value)

    def __validate_value__(self, value: T) -> T:
        if self.__rule__:
            self.__rule__(value)
        return value
        
    def __new_default__(self, value: Union[T, Callable[[], T]]):
        new_field = self.__clone__()
        new_field.__default__ = value
        new_field.get_default()
        return new_field

    def get_default(self) -> T:
        if callable(self.__default__):
            value = self.__default__()
        else:
            value = self.__default__

        return self.__normalize_value__(value)

        
    def __class_getitem__(self, args):
        class _TypedField(self):
            __type__ = args

        return _TypedField

    def __clone__(self):
        new_field = self.__class__(self.__default__)
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
    
    def __init__(self, default_keyset: dict = {}, **default_fields: Dict[str, Any]):
        defaults = {
            **default_keyset,
            **default_fields
        }
        
        for key, value in defaults.items():
            field: ABCField = self.__get_field__(key)
            self.__set_field__(key, field.__new_default__(value))

    def get_default(self) -> dict:
        defaults = {}
        for field_name in self.__metafields__:
            defaults[field_name] = self.__get_field__(field_name).get_default()
            if isinstance(defaults[field_name], ABCField):
                defaults[field_name] = defaults[field_name].get_default()
        return defaults

    def __set_field__(self, name, field: ABCField):
        self.__dict__[name] = field

    def __get_field__(self, name: str) -> ABCField:
        field = self.__dict__.get(name)
        if field is None:
            field = self.__class__.__dict__.get(name)
            if field is None:
                raise TypeError(f'{self.__class__.name} does not have field named {name}')
        
        if not isinstance(field, ABCField):
            raise TypeError(f'{self.__class__.__name__}\'s field {name} is not instance of Field')
        else:
            return field

    def __normalize_value__(self, dataset: dict) -> dict:
        if isinstance(dataset, self.__class__):
            return dataset.get_default()

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
    

class ABCSet(ABCField[T]):
    def __init__(self, default: Union[Iterable[T], Callable[[], Iterable[T]]] = None):
        super().__init__(default or [])

    def get_default(self) -> Tuple[T]:
        results = list()
        for val in super().get_default():
            if isinstance(val, ABCField):
                results.append(val.get_default())
            else:
                results.append(val)

        return results

    def __get__(self, instance, class_) -> Tuple[T]:
        return super().__get__(instance, class_)

    def __normalize_value__(self, dataset: Iterable[Any]) -> Tuple[T]:
        if issubclass(self.__type__, ABCFieldset) or issubclass(self.__type__, ABCSet):
                obj = self.__type__()
                return tuple(obj.__normalize_value__(value) for value in dataset)        
        else:
            resultset = list()
            for value in dataset:
                if not isinstance(value, self.__type__):
                    value = self.__type__(value)
                
                resultset.append(self.__validate_value__(value))

            return tuple(resultset)
            

class ABCMetaconfig(metaclass=MetaFieldset):
    def __init__(self, io_class = None):
        self.__io_class__ = io_class or 1 # TODO
        self.__default__ = None
        self.__type__ = None
        self.__name__ = self.__class__.__name__
        self.__label__ = ''
        self.__hint__ = ''
        self.__rule__: ABCRule = None
        self.__secret__ = False

    def get_default(self) -> dict:
        defaults = {}
        for field_name in self.__metafields__:
            defaults[field_name] = self.__class__.__dict__[field_name].get_default()
            if isinstance(defaults[field_name], ABCField):
                defaults[field_name] = defaults[field_name].get_default()
        return defaults
        # return [self.__class__.__dict__[field].get_default() for field in self.__metafields__]
        # return dict((field_name, self.__class__.__dict__[field_name].get_default()) for field_name in self.__metafields__)