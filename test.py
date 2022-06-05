from email.policy import default
from metaconfig import Field
from metaconfig.types import Fieldset, Set
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
    int_list = Set[int]((1,2,3)).rule(InRange(1,2))
    some_list = Set[Some]((Some(some=8),))
    list_some_list = Set[Set[Some]](((Some(some=9),),))

# print(Else().__normalize_value__({'some_else': {'some': "3"}}))
print(json.dumps(Else().get_default(), indent=2))
# print(Some().get_default())
# print()


