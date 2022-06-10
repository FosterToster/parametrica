from base64 import b64encode
import enum

from ..types import Field, Fieldset
from ..rules import InRange, Match


IP_MATCH = Match('^(?:(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])(\.(?!$)|$)){4}$')
DOMAIN_MATCH = Match('^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]$')
PATH_MATCH = Match('^(?:/[a-zA-Z0-9_\-]*)+$')


class IPField(Field[str]):
    def __new__(class_, *args, **kwargs):
        instance: Field = super().__new__(class_)
        instance.__init__(*args, **kwargs)
        instance.__rule__ = IP_MATCH
        return instance


class DomainField(Field[str]):
    def __new__(class_, *args, **kwargs):
        instance: Field = super().__new__(class_)
        instance.__init__(*args, **kwargs)
        instance.__rule__ = DOMAIN_MATCH
        return instance
    

class AnyHostField(Field[str]):
    def __new__(class_, *args, **kwargs):
        instance: Field = super().__new__(class_)
        instance.__init__(*args, **kwargs)
        instance.__rule__ = IP_MATCH | DOMAIN_MATCH
        return instance


class PortField(Field[int]):
    def __new__(class_, *args, **kwargs):
        instance: Field = super().__new__(class_)
        instance.__init__(*args, **kwargs)
        instance.__rule__ = InRange(0, 65535)
        return instance


class PathField(Field[str]):

    def __new__(class_, *args, **kwargs):
        instance: Field = super().__new__(class_)
        instance.__init__(*args, **kwargs)
        instance.__rule__ = PATH_MATCH
        return instance


class StrEnum(str, enum.Enum):
    
    @classmethod
    def _missing_(class_, value: object):
        value = str(value).strip().lower()
        for member in class_:
            if value == member.value:
                return member
        else:
            super()._missing_(value)


class Server(Fieldset):
    host = AnyHostField('0.0.0.0').label('Адрес сервера')
    port = PortField(0).label('Порт сервера')

    @property
    def address(self) -> str:
        '''host[:port]'''
        return f'{self.host}{":"+str(self.port) if self.port > 0 else ""}'

    @property
    def socket_addr(self):
        if self.port > 0:
            return (self.host, self.port)
        return self.host


class HTTPVariant(StrEnum):
    HTTP = 'http'
    HTTPS = 'https'  


class ProtocolHTTPVariant(Fieldset):
    protocol = Field[HTTPVariant](HTTPVariant.HTTPS).label('Протокол подключения').hint('HTTP/HTTPS')


class Credentials(Fieldset):
    user = Field[str]('').label('Логин пользователя')
    password = Field[str]('').label('Пароль пользователя')

    @property
    def auth(self) -> str:
        '''user:password'''
        return f'{self.user}:{self.password}'

    @property
    def auth_encoded(self) -> str:
        '''b64(user:password)'''
        return b64encode(self.auth.encode('utf-8')).decode('utf-8')

    @property
    def auth_header(self) -> str:
        '''Basic b64(user:password)'''
        return f'Basic {self.auth_encoded}'


class HTTPServer(Server, ProtocolHTTPVariant):

    url_prefix = PathField('/').label('URL префикс запросов').secret()
        
    @property
    def origin(self) -> str:
        '''protocol://host[:port]'''
        return f'{self.protocol.value}://{self.address}'

    def uri(self, method: str):
        '''/url_prefix/?method'''
        PATH_MATCH.try_check(method)
        return '/' + f'{self.url_prefix.strip("/")}/{method.strip("/")}'.strip('/')

    def endpoint(self, method: str):
        '''protocol://host[:port]/url_prefix/?method'''
        return f'{self.origin}{self.uri(method)}'


class BasicAuthHTTPServer(HTTPServer, Credentials):
    
    @property
    def auth_origin(self) -> str:
        '''protocol://user:password@host[:port]'''
        return f'{self.protocol.value}://{self.auth}@{self.address}'

    def auth_endpoint(self, method: str):
        '''protocol://user:password@host[:port]/url_prefix/?method'''
        return f'{self.auth_origin}{self.uri(method)}'