import enum
import json
from metaconfig import Field
from metaconfig.io import VirtualJsonFileConfigIO
from metaconfig import Fieldset, Metaconfig
from metaconfig import Match, Max, Min, InRange, MaxLen
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

config = Config(VirtualJsonFileConfigIO('conf.json'))


print(json.dumps(config.export(export_secret=False), indent=2, ensure_ascii=False))

