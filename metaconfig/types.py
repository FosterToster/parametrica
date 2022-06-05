from typing import Any, Dict, Type, Union, Callable, Iterable
from .abc import ABCField, ABCRule, ABCFieldset, ABCSet, ABCMetaconfig, T

class Field(ABCField[T]):

    # def __getattribute__(self, attr):
    #     original_value = super().__getattribute__(attr)
    #     if isinstance(original_value, Field):

    #     else:
    #         original_value
    def default(self, value: Union[T, Callable[[], T]]):
        new_field = self.__clone__()
        new_field.__default__ = value
        new_field.get_default()
        return new_field

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
        rule.type_check(self.__type__)
        new_field = self.__clone__()
        new_field.__rule__ = rule
        new_field.get_default()
        return new_field


class Fieldset(ABCFieldset):
    ...

class Set(ABCSet, Field):
    ...

class Metaconfig(ABCMetaconfig):
    ...
