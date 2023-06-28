from parametrica import ParametricaSingletone, Field
from parametrica.predefined.network import BasicAuthHTTPServer, Server
from parametrica.io import YAMLFileConfigIO

class NestedBasicAuthHTTPServer(BasicAuthHTTPServer):
    nested = Field[Server](host='109.202.22.231', port=55000).label('XML интерфейс связанной кассовой станции')

class Config(ParametricaSingletone):
    rk_server = Field[NestedBasicAuthHTTPServer](host="127.0.0.1", port=8091).label('Кассовый сервер r_keeper')
    local_server = Field[Server](port=2319).label('Локальный сервер')

config = Config(YAMLFileConfigIO('config.yaml', export_comments=True))
print('rk_server.address', config.rk_server.address )
print('rk_server.origin', config.rk_server.origin )
print('rk_server.auth', config.rk_server.auth )
print('Authorization:', config.rk_server.auth_header )
print('rk_server.endpoint', config.rk_server.endpoint('/wondeful/path') )
print()
print('local_server.address', config.local_server.address)