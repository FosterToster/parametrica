import unittest
from parametrica import Field, Fieldset

class TestFieldset(unittest.TestCase):
    
    def setUp(self) -> None:
        self.DEFAULT_STR = '0.0.0.0'
        self.FSTR = Field[str](self.DEFAULT_STR)
        self.DEFAULT_INT = 1234
        self.FINT = Field[int](self.DEFAULT_INT)
        
        class Server(Fieldset):
            host = self.FSTR
            port = self.FINT
        
        self.FIELDSET = Server

    def test_init_no_default(self):
        instance = self.FIELDSET()
        self.assertTrue(hasattr(instance, 'host'))
        self.assertTrue(hasattr(instance, 'port'))
        self.assertEqual(instance.host, self.DEFAULT_STR)
        self.assertEqual(instance.port, self.DEFAULT_INT)

    def test_init_default_kwarg(self):
        NEW_DEFAULT_STR = "192.168.1.1"
        instance = self.FIELDSET(host=NEW_DEFAULT_STR)
        self.assertEqual(instance.host, NEW_DEFAULT_STR)
        self.assertEqual(instance.port, self.DEFAULT_INT)

    def test_init_default_dict(self):
        NEW_DEFAULT_INT = 7894
        instance = self.FIELDSET({'port': NEW_DEFAULT_INT})
        self.assertEqual(instance.host, self.DEFAULT_STR)
        self.assertEqual(instance.port, NEW_DEFAULT_INT)

    def test_modify_field(self):
        with self.assertRaises(TypeError):
            instance = self.FIELDSET()
            instance.host = 'some'
    
    def test_modify_field_boilerplate(self):
        with self.assertRaises(TypeError):
            instance = self.FIELDSET()
            instance.host = 'some'

    def test_update_invalid(self):
        NEW_INT = 7894
        instance = self.FIELDSET()
        with self.assertRaises(ValueError):
            instance.__set_value__(NEW_INT)

    def test_update_field(self):
        NEW_INT = 7894
        instance = self.FIELDSET()
        instance.__set_value__({'port': NEW_INT})
        self.assertEqual(instance.port, NEW_INT)
    
    def test_update_field_misstype_valid(self):
        NEW_INT = '7894'
        instance = self.FIELDSET()
        instance.__set_value__({'port': NEW_INT})
        self.assertEqual(instance.port, int(NEW_INT))
    
    def test_update_field_misstype_invalid(self):
        NEW_NOT_INT = '7894a'
        instance = self.FIELDSET()
        with self.assertRaises(ValueError):
            instance.__set_value__({'port': NEW_NOT_INT})

    def test_inheritance(self):
        class CustomServer(self.FIELDSET):
            token = Field[str]('asdf')

        instance = CustomServer(host='109.202.22.22', token="8888")
        self.assertEqual(instance.host, '109.202.22.22')
        self.assertEqual(instance.port, self.DEFAULT_INT)
        self.assertEqual(instance.token, '8888')

    def test_custom_field(self):
        CUSTOM = '/one/two/three'

        class CustomServer(Fieldset):
            host = self.FSTR
            port = self.FINT
            path: str = CUSTOM
        
        instance = CustomServer()
        instance.__set_value__({'path': '/should/be/ignored'})
        self.assertEqual(instance.path, CUSTOM)

    def test_custom_method_return_self(self):
        class CustomServer(Fieldset):
            host = self.FSTR
            port = self.FINT

            def itself(self):
                return self
            
        instance = CustomServer()
        self.assertEqual(instance.itself(), instance)
    
    def test_custom_property_method(self):
        class CustomServer(self.FIELDSET):
            @property
            def socket_addr(self):
                return (self.host, self.port)
            
        instance = CustomServer()
        self.assertEqual(instance.socket_addr, (self.DEFAULT_STR, self.DEFAULT_INT))
       
    def test_get_not_field(self):
        class CustomServer(self.FIELDSET):
            @property
            def socket_addr(self):
                return (self.host, self.port)

        with self.assertRaises(TypeError):
            CustomServer().__get_field__('socket_addr')

    def test_get_undefined_field(self):
        class CustomServer(self.FIELDSET):
            @property
            def socket_addr(self):
                return (self.host, self.port)

        with self.assertRaises(TypeError):
            CustomServer().__get_field__('undefined_field')

        