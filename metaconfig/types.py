from distutils.log import error
from typing import Any, Dict, Tuple, Type, Union

from metaconfig.abc import Rule
from .io import JsonFileConfigIO, ConfigIOInterface


class MetaField(type):

    def __getitem__(class_, rules) -> Type['Field']:
        if not isinstance(rules, tuple):
            rules = (rules,)
        
        class _RuledFiled(Field):
            __rules__ = (*class_.__rules__, *rules)
        
        return _RuledFiled



class Field(metaclass=MetaField):
    __rules__ = tuple()
    
    @property
    def rules(self) -> Tuple[Rule]:
        return self.__rules__

    def __init__(self, label: str, hint: str = '') -> None:
        self.__label__ = label
        self.__default__ = None
        self.__hint__ = hint

    def __validate__(self, value: Any):
        for rule in self.rules:
            value = rule(value)        

        return value

    def __call__(self, default: Any) -> 'Field':
        self.__default__ = self.__validate__(default)
        return self


class MetaFieldSet(type):
    
    def __new__(class_, name, superclasses, dict_):
        if name == 'FieldSet':
            return super().__new__(class_, name, superclasses, dict_)

        class_instance = super().__new__(class_, name, superclasses, dict((k,v) for k,v in dict_.items() if not (isinstance(v, Field) or isinstance(v, FieldSet))))

        metamap: Dict[str, Union[Field, FieldSet]] = dict()

        newdict = dict()
        
        for cls in superclasses:
            if issubclass(cls, FieldSet):
                metamap.update(cls.__metamap__)

        for key, field in dict_.items():
            if isinstance(field, Field):
                metamap[f'.{key}'] = field
                
                if field.__default__ is None:
                    raise ValueError(f'{name}.{key} default value is not set. Usage: field: str = Field[*rules]("label","hint")(default_value)')

            elif isinstance(field, FieldSet):
                metamap[f'.{key}'] = field
                for mk, mv in field.__metamap__.items():
                    metamap[f'.{key}{mk}'] = mv
                    
                    if mv.__default__ is None:
                        raise ValueError(f'{name}.{key} default value is not set. Usage: field: str = Field[*rules]("label","hint")(default_value)')

            else:
                newdict[key] = field

        class_instance.__metamap__ = metamap

        return class_instance



class FieldSet(metaclass=MetaFieldSet):
    __metamap__: Dict[str, Field] = dict()
    
    def __init__(self, label: str, hint: str = '') -> None:
        self.__label__ = label
        self.__defaults__ = dict()
        self.__hint__ = hint

    def __default__(self, path:str):
        if path == '.':
            raise AttributeError(f'{self.__class__.__name__} can`t be used as default value')

        if hasattr(self, '__defaults__'):
            val = self.__defaults__.get(path) # try to get local default value
            if val is not None:
                return val

        # or get it from nested fields
        name, path_last =(*(path.split('.', 2)), '')[1:3]
        meta = self.__metamap__.get(f'.{name}')

        if isinstance(meta, FieldSet):
            return meta.__default__(f'.{path_last}')
        elif isinstance(meta, Field):
            if path_last:
                raise AttributeError(f'{self.__class__.__name__}.{name} does not have default value for "{path_last}"')
            return meta.__default__
        else:
            raise AttributeError(f'{self.__class__.__name__} does not have default value for {name}')

    def __call__(self, **defaults: Any):
        self.__defaults__ = dict((f'.{k}',v) for k,v in defaults.items())
        for path, value in self.__defaults__.items():
            value = self.__metamap__[path].__validate__(value)
        return self


class Metaconfig(FieldSet):
    def __init__(self, io_class: ConfigIOInterface = JsonFileConfigIO('settings.json')) -> None:
        self.__io_class__ = io_class
        pathset = self.__parsepathes__(self.__readstorage__(), '')
        self.__values__ = self.__validate_pathset__(pathset)
        self.__writestorage__(self.__serializepathes__(self.__values__))

    def __serializepathes__(self, pathset:Dict[str, Any]) -> dict:
        result = dict()
        for path, value in pathset.items():
            path_items = path.split('.')[1:]
            root_name = path_items.pop(0)
            result[root_name] = obj = result.get(root_name) or dict()

            if len(path_items) == 0:
                result[root_name] = value
                continue
            
            while len(path_items) > 1:
                key = path_items.pop(0)
                obj[key] = obj = obj.get(key) or dict()
            else:
                obj[path_items.pop(0)] = value

        return result
            
    def __validate_pathset__(self, pathset: dict):
        errors = dict()
        for path, value in pathset.items():
            try:
                value = self.__metamap__[path].__validate__(value)
            except ValueError as e:
                errors[path[1:]] = e
        if len(errors) == 0:
            return pathset
        else:
            raise ValueError('There is some configuration errors:\n'+'\n'.join([f'{path}: {e}' for path, e in errors.items()]))
    
    def __readstorage__(self) -> dict:
        try:
            return self.__io_class__.read()
        except FileNotFoundError:
            return self.__serializepathes__(dict((k, self.__default__(k)) for k,v in self.__metamap__.items() if isinstance(v, Field)))

    def __writestorage__(self, dataset: dict):
        return self.__io_class__.write(dataset)

    def __parsepathes__(self, dataset: dict, prefix: str) -> dict:
        result = dict()

        for k,v in dataset.items():
            if isinstance(v, dict):
                result.update(self.__parsepathes__(v, prefix + '.' + k))
            else:
                result[prefix + '.' + k] = v

        return result
