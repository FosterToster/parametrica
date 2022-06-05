from email.policy import default
from metaconfig import Field
from metaconfig.types import Fieldset
from metaconfig.rules import Max, Min, AND, OR, InRange, ABCRule
from dataclasses import dataclass


# print(ABCRule(1) >= ABCRule(2))

# print(MaxLen(6) + MinLen(2))
# print((MaxLen(6) | MinLen(2)) + InRange(2,6) )
# print(MaxLen(6) >= MinLen(2) )



# target behaviour

# class StrVal():
#     ...


# print(a.__annotations__)

# class Some:
#     one = Field[int](1)
#     two = Field[int](2)

class Config(Fieldset):
    some = Field[int](default=1).label('Тест').hint('Тестовое поле').rule(Min(5) + Max(50)).secret()
    

print(Config().some)


