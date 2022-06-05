from typing import Union, Callable, TypeVar, _GenericAlias, Generic
from dataclasses import dataclass
from .abc import ABCField, ABCRule, T

class Field(ABCField[T]):

    # def __getattribute__(self, attr):
    #     original_value = super().__getattribute__(attr)
    #     if isinstance(original_value, Field):

    #     else:
    #         original_value

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
        return new_field

    def __set_name__(self, value: str):
        self.__field_name__ = value


class MetaFieldset(type):

    def __new__(class_, name, bases, dict):
        for key, value in dict.items():
            if isinstance(value, Field):
                value.__field__name__ = key

        return super().__new__(class_, name, bases, dict)

@dataclass
class Fieldset(metaclass=MetaFieldset):
    ...
    