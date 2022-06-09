from typing import Type, Any

class MetaRule(type):

    def __getitem__(class_, restrictions) -> Type['ABCRule']:
        if not isinstance(restrictions, tuple):
            restrictions = (restrictions,)
            
        class _RestrictedRule(class_):
            __restrictions__ = (*class_.__restrictions__, *restrictions)

        return _RestrictedRule


class ABCRule(metaclass=MetaRule):
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

    def __str__(self):
        return f'{self.__class__.__name__}({self.value})'

    def type_check(self, type: Type[Any]):
        for t in self.restrictions:
            if issubclass(type, t):
                break
        else:
            raise TypeError(f'Field type "{type}" does not compatible with some assigned rules')