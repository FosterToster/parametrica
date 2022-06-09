from metaconfig import MetaconfigSingletone, Field
from metaconfig.predefined.network import BasicAuthHTTPServer, Server


class Config(MetaconfigSingletone):
    rk_server = Field[BasicAuthHTTPServer](host="127.0.0.1", port=8091)
    local_server = Field[Server](port=2319)

config = Config()
print('rk_server.address', config.rk_server.address )
print('rk_server.origin', config.rk_server.origin )
print('rk_server.auth', config.rk_server.auth )
print('Authorization:', config.rk_server.auth_header )
print('rk_server.endpoint', config.rk_server.endpoint('/wondeful/path') )
print()
print('local_server.address', config.local_server.address)