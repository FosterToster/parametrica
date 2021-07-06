# demo usage

from metaconfig import IntField, Fieldset, ConfigRoot, ListField

class ABSum(Fieldset):
    a:int = IntField(label='Значение А', default=1)
    b:int = IntField(label='Значение Б', default=2)


class Config(ConfigRoot):
    values = ListField(IntField, default=[IntField(label='', default=3), 3 , 5, '11'], label='Список чисел') 

config = Config()

for val in config.values:
    print(val)
