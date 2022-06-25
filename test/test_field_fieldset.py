import unittest
from metaconfig import Field, Fieldset

class TestFieldsetFields(unittest.TestCase):

    def setUp(self) -> None:
        class Server(Fieldset):
            host = Field[str]('0.0.0.0')
            port = Field[int](1234)

        self.FIELDSET = Server

    def test_init_no_default(self):
        instance = Field[self.FIELDSET]()
        isinstance(instance.__get_default__(), self.FIELDSET)
    
    def test_init_default_instance(self):
        DEFAULT_INSTANCE = self.FIELDSET(host="127.0.0.1")
        instance = Field[self.FIELDSET](DEFAULT_INSTANCE)
        isinstance(instance.__get_default__(), self.FIELDSET)
        self.assertEqual(instance.__get_default__().host, "127.0.0.1")
    
    def test_init_default_kwarg(self):
        instance = Field[self.FIELDSET](port=8888)
        self.assertEqual(instance.__get_default__().port, 8888)

    def test_inside_fieldset(self):
        class ServerContainer(Fieldset):
            server = Field[self.FIELDSET]()

        self.assertEqual(ServerContainer().server.host, '0.0.0.0')
    
    def test_inside_fieldset_default_instance(self):
        class ServerContainer(Fieldset):
            server = Field[self.FIELDSET]()

        self.assertEqual(
            ServerContainer(
                server=self.FIELDSET(
                    host='127.0.0.1'
                )
            ).server.host, 
            '127.0.0.1'
        )

    def test_inside_fieldset_set_value(self):
        class ServerContainer(Fieldset):
            server = Field[self.FIELDSET]()

        instance = ServerContainer()
        instance.__set_value__({'server': {'host': "127.0.0.1"}})

        self.assertEqual(instance.server.host, '127.0.0.1')
    
