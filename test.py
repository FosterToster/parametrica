from email.policy import default
from metaconfig import Field
from metaconfig.types import Fieldset, Set, Metaconfig
from metaconfig.rules import Max, Min, AND, OR, InRange, ABCRule
from dataclasses import dataclass
import json


# print(ABCRule(1) >= ABCRule(2))

# print(MaxLen(6) + MinLen(2))
# print((MaxLen(6) | MinLen(2)) + InRange(2,6) )
# print(MaxLen(6) >= MinLen(2) )



# target behaviour

class Some(Fieldset):
    some = Field[int](10)\
        .label('Тест')\
        .hint('Тестовое поле')\
        .rule(InRange(5,10))\
        .secret()


# print(callable(Some()))  
class Else(Fieldset):
    some_else = Field[Some](Some(some=5)).label('Дарова')
    int_list = Set[int]((1,2,3)).rule(InRange(1,3))
    some_list = Set[Some]((Some(some=8), Some(some=10)))


class Config(Metaconfig):
    __data__ = {'do': True, 'some': {'some': 10}, 'else_': {'some_else': {'some': 5}, 'int_list': [1, 2, 3], 'some_list': [{'some': 8}, {'some': 10}]}}

    do = Field[bool](True)
    some = Field[Some]()
    else_ = Field[Else]()
    
# print(Else().__normalize_value__({'some_else': {'some': "3"}}))
# print(json.dumps(Config().get_default(), indent=2))
print(Config().get_default())
# print()


