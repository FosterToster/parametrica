from typing import List, Tuple, Any, Type
from .abc import ABCRule
import re

class Rule(ABCRule):
    def __add__(self, other: 'ABCRule') -> 'ABCRule':
        return AND(self, other)
    
    def __or__(self, other: 'ABCRule') -> 'ABCRule':
        return OR(self, other)


class Multirule(Rule):
    def __init__(self, *rules: Tuple[ABCRule]) -> None:
        extends = []
        for rule in rules:
            if isinstance(rule, self.__class__):
                extends.extend(rule.__rules__)
            else:
                extends.append(rule)
        
        self.__rules__: Tuple[ABCRule] = extends

    def __str__(self):
        return f'{self.__class__.__name__}({", ".join(str(x) for x in self.__rules__)})'

    def type_check(self, type: Type[Any]):
        for rule in self.__rules__:
            rule.type_check(type)
            

class AND(Multirule):

    def try_check(self, value: Any) -> Any:
        for rule in self.__rules__:
            rule(value)


class OR(Multirule):

    def try_check(self, value: Any) -> Any:
        for rule in self.__rules__:
            try:
                return rule.try_check(value) or value
            except ValueError:
                continue
        else:
            raise ValueError(f'The value "{value}" does not satisfying no one of required rules')


class Min(Rule[int]):
   
    def try_check(self, value: int) -> bool:
        if value < self.value:
            raise ValueError(f'Value can`t be less than {self.value}')


class Max(Rule[int]):
   
    def try_check(self, value: int) -> bool:
        if value > self.value:
            raise ValueError(f'Value can`t be greater than {self.value}')


class InRange(Rule[int]):
    def __init__(self, min: int, max: int) -> None:
        self.value = (min, max)
        self.min = Min(min)
        self.max = Max(max)
    
    def try_check(self, value):
        self.min.try_check(value)
        self.max.try_check(value)


class MinLen(Rule[list, str]):

    def try_check(self, value):
        if len(value) < self.value:
            raise ValueError(f'Length can`t be less than {self.value}')


class MaxLen(Rule[list, str]):

    def try_check(self, value):
        if len(value) > self.value:
            raise ValueError(f'Length can`t be more than {self.value}')


class Match(Rule[str]):
    def __init__(self, mask: str) -> None:
        self.value = mask
        self.regex = re.compile(mask)

    def try_check(self, value):
        if self.regex.match(value) is None:
            raise ValueError('Value is not matching required mask.')
        