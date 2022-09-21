from typing import Any, Dict

from .field import ABCField

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
    
    def __init__(self, default_keyset: dict = {}, **default_fields: Dict[str, Any]):
        defaults = {
            **default_keyset,
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
        if not isinstance(dataset, dict):
            raise ValueError(f'Invalid dataset structure. Object type required for this field.')
        new_fieldset = self.__clone__()
        for field_name, value in dataset.items():
            if not field_name in self.__metafields__:
                continue
            field: ABCField = new_fieldset.__get_field__(field_name)
            # try:
            new_fieldset.__set_field__(field_name, field.__set_value__(value, new_fieldset))
            # except ValueError as e:
            #     raise ValueError(f'{new_fieldset.__class__.__name__} -> {e}') from e
        
        return new_fieldset

    def __export_data__(self, instance: '_FieldRW', *, export_secret: bool = False):
        result = {}
        for field_name in self.__metafields__:
            field = self.__get_field__(field_name)
            if not export_secret and field.__secret__:
                continue
            result[field_name] = field.__export_data__(self, export_secret=export_secret)

        return result

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

    def __metadata__(self, instance: _FieldRW):
        metadata = dict()
        for field_name in self.__metafields__:
            field = self.__get_field__(field_name)
            metadata[field_name] = field.__metadata__(self)
        return metadata

    

class ABCMetaconfig(_FieldRW, metaclass=MetaFieldset):
    def _initialize(self, io_class: 'ConfigIOInterface'):
        self.__name__ = ''
        self.__io_class__ = io_class
        self.__io_class__.parent = self

        try:
            dataset = self.__io_class__.read()
            self.__update__(dataset)        
        except FileNotFoundError:
            self.__write__()
        else:
            self.__write__()
        
    def __write__(self):
        self.__io_class__.write( self.__dataset__() )

    def __dataset__(self,*, export_secret: bool = False) -> dict:
        result = {}
        for field_name in self.__metafields__:
            field = self.__get_field__(field_name)
            if (not export_secret) and field.__secret__:
                continue
            result[field_name] = field.__export_data__(self, export_secret=export_secret)

        return result
        # return dict((field_name, self.__get_field__(field_name).__export_data__(self, export_sercet=export_sercet)) for field_name in self.__metafields__)
    
    def __metadata__(self) -> dict:
        metadata = dict()
        for field_name in self.__metafields__:
            field = self.__get_field__(field_name)
            metadata[field_name] = field.__metadata__(self)

        return metadata

    def __update__(self, dataset: dict):
        for field_name, value in dataset.items():
            if not field_name in self.__metafields__:
                continue
            field: ABCField = self.__get_field__(field_name)
            try:
                self.__set_field__(field_name, field.__set_value__(value, self))
            except ValueError as e:
                raise ValueError(f'{self.__class__.__name__} -> {e}') from e


from ..io import ConfigIOInterface