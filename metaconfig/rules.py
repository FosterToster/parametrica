from .abc import Rule
import re

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
        self.min = Min(min)
        self.max = Max(max)
    
    def try_check(self, value):
        self.min.try_check(value)
        self.max.try_check(value)


class MinLen(Rule[list, str]):

    def try_check(self, value):
        if len(value) < self.value:
            raise ValueError(f'Length can`t be less than {self.value}')


class MinLen(Rule[list, str]):

    def try_check(self, value):
        if len(value) > self.value:
            raise ValueError(f'Length can`t be more than {self.value}')


class Match(Rule[str]):
    def __init__(self, mask: str) -> None:
        self.regex = re.compile(mask)

    def try_check(self, value):
        if self.regex.match(value) is None:
            raise ValueError('Value is not matching required mask.')
        