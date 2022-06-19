# Parametrica

## What is it?
Parametrica is an ORM for application configurations.\
With it you will able to define your configuration schema in the easiest way!


## Basic example

```python
# [config.py]
from parametrica import Field, Fieldset, Parametrica, InRange, io.JsonFileConfigIO

# Let`s define an Server fieldset
class Server(Fieldset):
    host = Field[str](default='0.0.0.0').label('Server address')
    port = Field[int](default=0).label('Server port').rule(InRange(0, 65535))

# Inheritance is also supported
class AuthServer(Server):
    user = Field[str]('admin').label('Username')
    password = Field[str]('P@55\/\/0rd').lable('Password')

# Finally, define a configuration root
class Config(Parametrica):
    api_server = Field[AuthServer](host="any.api.com", port="443").label('API Server')
    local_server = Field[Server](port=8080).label('Local server')

    # of course, you can define any field in the config root
    deferred_startup = Field[bool](False).label('Start server after 10 secs')



#[app.py]
from config import Config
from server import SomeLocalServer
from api_helper improt SomeApiHelper

# initialize your config
if __name__ == "__main__":
    try:
        config = Config(JsonFileConfigIo('my_config.json'))
    except (TypeError, ValueError) as e:
        # don`t forget about possible errors
        print(f'Looks like current application config is invalid: {e}')
    else:
        # and enjoy your config
        api_client = SomeApiHelper(config.api_server)
        local_server = SomeLocalServer(api_client, config.local_server)

        if config.deferred_startup:
            sleep(10)

        local_server.run()
```
