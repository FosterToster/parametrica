from typing import Any, Dict, Type, Union


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
    def rules(self):
        return self.__rules__

    def __init__(self, label: str, hint: str = '') -> None:
        self.__label__ = label
        self.__default__ = None
        self.__hint__ = hint

    def __call__(self, default: Any) -> 'Field':
        self.__default__ = default
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
    __metamap__ = dict()
    
    def __init__(self, label: str, hint: str = '') -> None:
        self.__label__ = label
        self.__defaults__ = dict()
        self.__hint__ = hint

    def __default__(self, path:str):
        if path == '.':
            raise AttributeError(f'{self.__class__.__name__} can`t be used as default value')

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
        return self