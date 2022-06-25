import unittest
from typing import Tuple
from metaconfig import Field, Fieldset

class TestFieldsetIterableField(unittest.TestCase):

    class FIELDSET(Fieldset):
        host = Field[str]('0.0.0.0')
        port = Field[int](1234)

    def test_init_no_default(self):
        instance = Field[Tuple[self.FIELDSET]]()
        self.assertTrue(isinstance(instance.__get_default__(), tuple))

    def test_init_default_kwarg(self):
        instance = Field[Tuple[self.FIELDSET]](host="127.0.0.1")
        self.assertTrue(isinstance(instance.__get_default__(), tuple))
        self.assertTrue(isinstance(instance.__get_default__()[0], self.FIELDSET))
        self.assertEqual(instance.__get_default__()[0].host, '127.0.0.1')

    def test_init_default_instance(self):
        instance = Field[Tuple[self.FIELDSET]](self.FIELDSET( port=8888 ))
        self.assertTrue(isinstance(instance.__get_default__(), tuple))
        self.assertTrue(isinstance(instance.__get_default__()[0], self.FIELDSET))
        self.assertEqual(instance.__get_default__()[0].port, 8888)
    
    def test_init_default_iterable(self):
        instance = Field[Tuple[self.FIELDSET]]([self.FIELDSET( port=8888 ), self.FIELDSET(host='127.0.0.1')])
        self.assertTrue(isinstance(instance.__get_default__(), tuple))
        self.assertTrue(isinstance(instance.__get_default__()[0], self.FIELDSET))
        self.assertTrue(isinstance(instance.__get_default__()[1], self.FIELDSET))
        self.assertEqual(instance.__get_default__()[0].host, '0.0.0.0')
        self.assertEqual(instance.__get_default__()[0].port, 8888)
        self.assertEqual(instance.__get_default__()[1].host, '127.0.0.1')
        self.assertEqual(instance.__get_default__()[1].port, 1234)
    
    def test_inside_fieldset(self):
        class ServerPool(Fieldset):
            servers = Field[Tuple[self.FIELDSET]]()

        self.assertTrue(isinstance(ServerPool().servers, tuple))
    
    def test_inside_fieldset_set_value(self):
        class ServerPool(Fieldset):
            servers = Field[Tuple[self.FIELDSET]]()

        instance = ServerPool()

        instance.__set_value__({'servers': [{'host': "127.0.0.1", 'port': 8888}]})

        self.assertTrue(instance.servers, tuple)
        self.assertEqual(instance.servers[0].host, '127.0.0.1')
        self.assertEqual(instance.servers[0].port, 8888)

    def test_inside_fieldset_set_value_not_iterable(self):
        class ServerPool(Fieldset):
            servers = Field[Tuple[self.FIELDSET]]()

        instance = ServerPool()

        instance.__set_value__({'servers': {'host': "127.0.0.1", 'port': 8888}})

        self.assertTrue(instance.servers, tuple)
        self.assertEqual(instance.servers[0].host, '127.0.0.1')
        self.assertEqual(instance.servers[0].port, 8888)
    
    def test_inside_fieldset_set_two_values(self):
        class ServerPool(Fieldset):
            servers = Field[Tuple[self.FIELDSET]]()

        instance = ServerPool()

        instance.__set_value__({'servers': [{'host': "127.0.0.1", 'port': 8888},{'host': "192.168.1.1", 'port': 9999}]})

        self.assertTrue(instance.servers, tuple)
        self.assertEqual(instance.servers[0].host, '127.0.0.1')
        self.assertEqual(instance.servers[0].port, 8888)
        self.assertEqual(instance.servers[1].host, '192.168.1.1')
        self.assertEqual(instance.servers[1].port, 9999)

    def test_inside_fieldset_two_defaults_set_value(self):
        class ServerPool(Fieldset):
            servers = Field[Tuple[self.FIELDSET]]([self.FIELDSET(host="127.0.0.1"), self.FIELDSET(port=9999)])

        instance = ServerPool()

        instance.__set_value__({'servers': [{'host': "127.0.0.1", 'port': 8888}]})

        self.assertTrue(instance.servers, tuple)
        self.assertEqual(instance.servers[0].host, '127.0.0.1')
        self.assertEqual(instance.servers[0].port, 8888)