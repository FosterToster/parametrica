from typing import Any, Dict, Type, Union, Callable, Iterable
from .abc import ABCField, ABCRule, ABCFieldset, ABCMetaconfig, T

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


class Fieldset(ABCFieldset):
    ...


class Metaconfig(ABCMetaconfig):
    ...
