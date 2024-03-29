![Logo](/wiki/Logo.png?raw=true)

<hr>

What is it?\
Parametrica is an ORM for application configurations.\
With it you will able to define your configuration schema in the easiest way!

## <span name="head-1">Basic example</span>
`./config.py`
```python
from parametrica import Field, Fieldset, Parametrica, InRange, io.JsonFileConfigIO

#Let`s define a Server fieldset
class Server(Fieldset):
    host = Field[str](default='0.0.0.0').label('Server address')
    port = Field[int](default=0).label('Server port').rule(InRange(0, 65535))

#Inheritance is also supported
class AuthServer(Server):
    user = Field[str]('admin').label('Username')
    password = Field[str]('P@55\/\/0rd').lable('Password')

#Finally, define a configuration root
class Config(Parametrica):
    api_server = Field[AuthServer](host="any.api.com", port="443").label('API Server')
    local_server = Field[Server](port=8080).label('Local server')

    #of course, you can define any field in the config root
    deferred_startup = Field[bool](False).label('Start server after 10 secs')

```
`./app.py`
```python
from config import Config
from server import SomeLocalServer
from api_helper improt SomeApiHelper


if __name__ == "__main__":
    # initialize your config
    try:
        config = Config(JsonFileConfigIo('my_config.json'))
    except (TypeError, ValueError) as e:
        # don`t forget about possible errors
        print(f'Looks like current application config is invalid: {e}')
    else:
        # and enjoy
        api_client = SomeApiHelper(config.api_server)
        local_server = SomeLocalServer(api_client, config.local_server)

        if config.deferred_startup:
            sleep(10)

        local_server.run()
```
# Table of contents
- [Utility classes](#head-2)
  - [class "Fieldset"](#head-3)
  - [class "Field"](#head-4)
    - [Value normalization](#head-14)
    - [Methods](#head-6)
      - [label](#head-7)
      - [hint](#head-8)
      - [secret](#head-9)
      - [rule](#head-10)
      - [default](#head-11)
    - [Usage](#head-12)
      - [With Primitive types](#head-13)
        
      - [With Fieldset children](#head-15)
      - [With "typing" iterables](#head-16)
  - [class "Parametrica"](#head-17)
    - [IO classes](#head-18)



# <span name="head-2">Utility classes</span>
There are several utility classes for defining a configuration schema: `Field`, `Fieldset`, `Parametrica` and `Rule` children.

## <span name="head-3">class `Fieldset`</span>
This is an abstract class used to be universal parent for all classes 

## <span name="head-4">class `Field[T]`</span>

`Field` is a generic class.\
Its generic agrument defines which type will be contained in field instance.\
Currently supported types:
  - Primitive:
    - `str`
    - `int`
    - `bool`
    - `float`
  - `enum.Enum` types (interpretes as primitive)
  - `Fieldset` children
  - `typing` module iterables:
    - `Iterable[T]`
    - `Tuple[T]`
    - `List[T]`

Every `Field` must be instantiatied with generic argument and assigned with static field of `Fieldset` or `Parametrica` child.\
Eventually it will be interpreted as model field definition.\
Init arg of field defines its default value.

This record:
```python
class Model(Fieldset):
    name = Field[str]('John Doe')
```
means that we have some fieldset `Model` which is have the only field **_name_** of type `str` with default value **_John Doe_**

Also you can pass a `callable` as init argument instead of explicit value.\
It does'nt take any args, but should return default value of field's type.

In common case default value, or `callable` return type, should equals with field's generic agrument, but it is not strict rule because of **_value normalization principle_**

### <span name="head-14">Value normalization principle</span>

Fields will always try to cast values to its generic type simply by wrapping value with it (for default values and `callable` results too)\
It works like that:
```python
def normalize(type_: Type[T], value: Any) -> T:
    return type_(value)

raw = '1234'
T = int
normalized: T = normalize(T, raw) # int('1234')
assert isinstance(normalized, T)
```
So, below example is also correct because `bool(1) == True`
```python
#CORRECT
Field[bool](1)
```
This principle guarantees that you will always have value of expected type in your field.\
It may be necessary for comparison.


### <span name="head-6">Methods:</span>
`Field` instance have some utility methods to provide additional information about itself.\
They`re meant to be called in chain stight after initialization.\
**Be careful!** Every utility method will **clone** current instance and return it modified.

#### <span name="head-7">.label(text: str)</span>
Add a human-readable label for field
```python
Field[str]('John Doe').label('Default customer name')
```

#### <span name="head-8">.hint(text: str)</span>
Add more explanations for field purpose or its specific values
```python
Field[str]('John Doe').label('Default customer name')\
    .hint('This name will be assigned to each customer record created automatically')
```

#### <span name="head-9">.secret(value: bool = True)</span>
Make field secret (or not - depends on value)\
Secret fields will not be exported to persistent storage until they was expicitly modified.
```python
Field[str]('John Doe').label('Default customer name').secret()
```

#### <span name="head-10">.rule(rule: ABCRule)</span>
Add a rule for field value.\
Calling this method will cause type-check for passed rule and field`s generic argument.\
**TypeError** will be raised if passed rule does not support values of field's type
```python
Field[int](8080).label('TCP Port').rule( InRange(0, 65535) )
```

#### <span name="head-11">.default(value: Union[T, Callable[[], T]])</span>
Override default value passed with initialization.\
It can be useful if you've created a common field to use it in different fieldsets, and you need replace default value in special case.
```python
#define a common field
PortField = Field[int](8080).label('Server port').rule(InRange(0, 65535))

#Use it in a common case
class ApiServer(FieldSet):
    port = PortField

#Use it in a special case
class LocalServer(Fieldset):
    port = PortField.default(lambda: input('Type local server port (0..65535): '))

```
### <span name="head-12">Usage</span>
#### <span name="head-13">With Primitive types</span>
Each `Field ` of primitive type must be initialized with default value.\
```python
#WRONG
Field[bool]() # raises ValueError

#CORRECT
Field[bool](False)
```

#### <span name="head-15">With Fieldset children</span>
`Field` of type which is inherited from `Fieldset` does not require any default value because all defaults alredy been defined in its type.\
But you always able to override it by two similar ways:
  - By `Fieldset` instance\
  Just pass instance of your fieldset as default value on `Field` initialization
  ```python
  class Common(Fieldset):
    value = Field[str]('default value')

  Field[Common](Common(value='default overridden'))
  ```
  - implicit initialization\
  Initialize `Field` with kwargs which are matches `Fieldset`'s field names\
  This feature makes code a little more readable.\
  Under the hood it works exatly like previous example.
  ```python
  class Common(Fieldset):
    key = Field[str]('default key')
    value = Field[str]('default value')

  Field[Common](value='default value overridden')
  ```

#### <span name="head-16">With `typing` iterables</span>
Usage with iterable fields is very similar, but it also supports iterables as default value.\

The rules of initialization with primitive or `Fieldset` types are also the same but here is several nuances:
  - default value for primitive iterables is not required.
  - rules passed for iterable fields acts for each item, not for field.
  - If default value is passed, but it is not iterable, it will be interpreted as default for first item of iterable value.
  - All of supported typing iterable types will be converted to tuple on reading

Some examples:
```python
from parametrica import Max, Fieldset, Parametrica
from typing import List, Iterable, Tuple

#Fieldset child class
class Server(Fieldset):
    host = Field[str](default='0.0.0.0')
    port = Field[int](default=0).rule(InRange(0, 65535))


#config root
class IterableExamples(Parametrica):
    # list of integers. Empty by default.
    # Each item in list must be less or equal 10
    empty_integer_list = Field[List[int]]().rule(Max(10))

    # list of floats. 
    # Contans single item with value 0.3 by default
    default_float_list = Field[Iterable[float]](.3)

    # empty list of `Server`s.
    empty_server_pool = Field[Iterable[Server]]()

    # list of `Server`s.
    # first item will have default host and port
    default_server_pool = Field[Tuple[Server]](host="127.0.0.1", port=8080)

    # list of `Server`s.
    # first two items will have different default host and port
    two_defaults_server_pool = Field[List[Server]](
        (
            Server(host="127.0.0.1", port=8080),
            Server(host="localhost", port=9090)
        )
    )

#All iterable fields become tuples when you try to read it
assert isinstance(IterableExamples().empty_integer_list, tuple)
assert isinstance(IterableExamples().default_float_list, tuple)
assert isinstance(IterableExamples().empty_server_pool, tuple)
assert isinstance(IterableExamples().default_server_pool, tuple)
assert isinstance(IterableExamples().two_defaults_server_pool, tuple)

```

## <span name="head-17">class `Parametrica`</span>
#TODO
### <span name="head-18">IO classes</span>
#TODO
