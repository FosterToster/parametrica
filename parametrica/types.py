from typing import Any, Dict, Type, Union, Callable, Iterable
from .abc import ABCField, ABCRule, ABCFieldset, ABCMetaconfig, T
from .io import ConfigIOInterface, JsonFileConfigIO

class Field(ABCField[T]):

    def default(self, value: Union[T, Callable[[], T]]):
        return self.__clone__(value)

    def label(self, text: str):
        '''
        Set a label for field
        '''
        new_field = self.__clone__()
        new_field.__label__ = text
        return new_field

    def hint(self, text: str):
        '''
        Set a hint for field
        '''
        new_field = self.__clone__()
        new_field.__hint__ = text
        return new_field

    def secret(self, value: bool = True):
        '''
        Set secret property for field
        '''

        new_field = self.__clone__()
        new_field.__secret__ = value
        return new_field

    def rule(self, rule: ABCRule):
        '''
        Assign validation rule for field
        '''
        rule.type_check(self.__generic_type__())
        new_field = self.__clone__()
        new_field.__rule__ = rule
        new_field.__get_default__()
        return new_field
    
    def password(self, value: bool = True):
        '''
        Set password property for field
        '''
        new_field = self.__clone__()
        new_field.__password__ = value
        return new_field


class Fieldset(ABCFieldset):
    ...


class Parametrica(ABCMetaconfig):

    def __init__(self, io_class: ConfigIOInterface = JsonFileConfigIO('settings.json')) -> None:
        self._initialize(io_class)

    def export(self, *, export_secret: bool = False) -> dict:
        return self.__dataset__(export_secret=export_secret)

    def update(self, dataset: dict):
        self.__update__(dataset)
        self.__write__()


class ParametricaSingletone(Parametrica):
    def __init__(self, io_class: ConfigIOInterface = JsonFileConfigIO('settings.json')) -> None:
        ...

    def __new__(class_, io_class: ConfigIOInterface = JsonFileConfigIO('settings.json')):
        if hasattr(class_, '__instance__'):
            return class_.__instance__

        class_.__instance__ = super().__new__(class_)
        class_.__instance__._initialize(io_class)
        return class_.__instance__
