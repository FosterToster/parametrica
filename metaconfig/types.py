from typing import Any, Dict, Type, Union


class MetaField(type):

    def __getitem__(class_, *rules) -> Type['Field']:
        class _RuledFiled(Field):
            __rules__ = tuple(rules)
        
        return _RuledFiled



class Field(metaclass=MetaField):
    __rules__ = tuple()
    
    @property
    def rules(self):
        return self.__rules__

    def __init__(self, *, label: str, default: Any, hint: str = '') -> None:
        self.label = label
        self.default = default
        self.hint = hint


class MetaFieldSet(type):
    
    def __new__(class_, name, superclasses, dict_):
        if name == 'FieldSet':
            return super().__new__(class_, name, superclasses, dict_)

        newdict = dict()
        newdict['__metamap__'] = dict()
        for cls in superclasses:
            if issubclass(cls, FieldSet):
                newdict['__metamap__'].update(cls.__metamap__)

        for k,v in dict_.items():
            if isinstance(v, Field):
                newdict['__metamap__'][f'.{k}'] = v
            elif isinstance(v, FieldSet):
                newdict['__metamap__'][f'.{k}'] = v
                for mk, mv in v.__metamap__.items():
                    newdict['__metamap__'][f'.{k}{mk}'] = mv
            else:
                newdict[k] = v

        return super().__new__(class_, name, superclasses, newdict)



class FieldSet(metaclass=MetaFieldSet):
    __metamap__ = dict()
    
    def __init__(self, *, label: str, hint: str = '') -> None:
        self.label = label
        self.defaults = None
        self.hint = hint

    def __call__(self, **defaults: Any):
        self.defaults = defaults
        return self