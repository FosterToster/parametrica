import enum
import json
from metaconfig import Field
from metaconfig.types import Fieldset, Metaconfig
from metaconfig.rules import Match, Max, Min, InRange, ABCRule, MaxLen
from typing import Iterable, List, Tuple


# target behaviour

# Объявили поле - порт с соответствующими правилами
PortField = Field[int](0).rule(InRange(0, 65535))
HostField = Field[str]('0.0.0.0').rule(Match('^(?:(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(?!$)|$)){4}$'))


# Объявили базовый класс для сервера
class Server(Fieldset):
    # Заюзали, откаментили
    host = HostField.label('Хост адрес сервера').hint('IP адрес компьютера, на котром работает сервер')
    # Заюзали, откаментили
    port = PortField.label('Порт адрес сервера')


class Protocol(str, enum.Enum):
    TCP = 'tcp'
    HTTP = 'http'
    HTTPS = 'https'

ProtocolField = Field[Protocol](Protocol.TCP).label('Протокол сервера')


# Унаследовали Server, добавили поле protocol
class ProtocolServer(Server):
    # Пометили как секретное
    protocol = ProtocolField.secret()

class Credentials(Fieldset):
    user = Field[str]('').label('Логин пользователя').rule(MaxLen(10))
    pwd = Field[str]('').label('Пароль пользователя')

# Унаследовали ProtocolServer, добавили строковых полей
class AuthHTTPServer(ProtocolServer):
    host = HostField.default('192.168.1.100')
    port = PortField.default(8080)
    credentials = Field[Credentials](user="carbis", pwd=1234)

class Printer(Fieldset):
    # заюзали старое поле с новым дефолтом
    port = PortField.default(1000).label('Порт принтера')
    name = Field[str]('Принтер').label('Название принтера')


# корень конфига
class Config(Metaconfig):
    # Обявили поле типа str с дефолтным значением 12 (автоматические приведение типа, на выходе будет str)
    how_many = Field[str](13)
    # Обявили поле типа Server, задали дефолтное значение поля прямо в Field
    local_server = Field[Server](host="192.168.1.100", port=11010)
    # Но можно и так
    # local_server = Field[Server](Server(port=11010))
    # Обявили поле типа AuthHTTPServer, задали дефолтное значение для унаследованного! поля
    r_keeper = Field[AuthHTTPServer](protocol=Protocol.HTTPS)
    # задали пустой список примитивов c максимальным значением 5
    counts = Field[Iterable[int]]().rule(Max(5))
    # задали список Fieldset'ов. Инициализация дефолтного работает втч напрямую в Field
    printers = Field[List[Printer]](name="Хороший принтер", port=5152).label('asdf')    
    # задали массив строк с двумя значениеями по-умолчанию
    data = Field[Tuple[str]](['Привет', 'Мир'])

config = Config()
# print( 'config.how_many ', config.how_many )
# print( 'config.local_server.host ', config.local_server.host )
# print( 'config.local_server.port ', config.local_server.port )
# print( 'config.r_keeper.protocol ', config.r_keeper.protocol )
# print( 'config.r_keeper.credentials.user ', config.r_keeper.credentials.user )
# print( 'config.r_keeper.credentials.pwd ', config.r_keeper.credentials.pwd )
# print( 'config.counts ', config.counts )
# print( 'config.printers[0].name ', config.printers[0].name )
# print( 'config.printers[0].port ', config.printers[0].port )
# print( 'config.data', config.data)
# print()
# config.update({
#     'how_many': "Привет",
#     "local_server": {
#         "host": "192.168.1.1",
#         "port": "2212"
#     },
#     "r_keeper": {
#         'protocol': 'tcp',
#         'credentials': {
#             'user': "momaафаф",
#             'pwd': "1",
#         }
#     },
#     "counts": [1,2,5],
#     "printers": [
#         {},
#         {
#             "name": "Принтер великолепный"
#         },
    
#     ],
#     "data": ["Hello", "world"]

# })

print(json.dumps(config.export(), indent=2, ensure_ascii=False))

# print( 'config.how_many ', config.how_many )
# print( 'config.local_server.host ', config.local_server.host )
# print( 'config.local_server.port ', config.local_server.port )
# print( 'config.r_keeper.protocol ', config.r_keeper.protocol )
# print( 'config.r_keeper.credentials.user ', config.r_keeper.credentials.user )
# print( 'config.r_keeper.credentials.pwd ', config.r_keeper.credentials.pwd )
# print( 'config.counts ', config.counts )
# print( 'config.printers[0].name ', config.printers[0].name )
# print( 'config.printers[0].port ', config.printers[0].port )
# print( 'config.printers[1].name ', config.printers[1].name )
# print( 'config.printers[1].port ', config.printers[1].port )
# print( 'config.data', config.data)


