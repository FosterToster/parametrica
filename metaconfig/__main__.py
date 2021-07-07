# demo usage
import json
from metaconfig.types import StrField
from metaconfig import IntField, Fieldset, ConfigRoot, ListField

class HostPort(Fieldset):
    host = StrField(label='Хост', default='0.0.0.0')
    port = IntField(label='Порт', default=11000)

class ABSum(Fieldset):
    a:int = IntField(label='Значение А', default=1)
    b:int = IntField(label='Значение Б', default=2)
    hosts = ListField(HostPort(label='Кассовый сервер'), default=[{'host': '192.168.1.100', 'port':15151}], label='Кассовые сервера')


class Config(ConfigRoot):
    sums = ABSum(label= 'Some A and B')
    values = ListField(IntField(label="Some integer", default=0), default=[3 , 5, '11'], label='Список чисел') 

config = Config()

print(json.dumps(config.as_metadata(), indent=2))

for val in config.values:
    print(val)

print(config.sums.a)
print(config.sums.b)
