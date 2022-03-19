from typing import Any, Type
       
class MetaRule(type):

    def __getitem__(class_, *restrictions) -> Type['Rule']:
        class _RestrictedRule(Rule):
            __restrictions__ = tuple(restrictions)

        return _RestrictedRule


class Rule(metaclass=MetaRule):
    __restrictions__ = tuple()

    def __init__(self, value: Any) -> None:
        self.value = value

    @property
    def restrictions(self):
        return self.__restrictions__
    
    def try_check(self, value: Any) -> Any:
        ...

    def __call__(self, value: Any) -> Any:
        r = self.try_check(value)
        return r or value