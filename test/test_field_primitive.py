from metaconfig.types import Field, ABCField
from enum import Enum
import unittest

class TestInvalidType(unittest.TestCase):
    def test_invalid_type(self):
        with self.assertRaises(TypeError):
            Field[dict]({})

class TestIntField(unittest.TestCase):
    T = int
    DEFAULT = 1234
    DEFAULT_MISSTYPE_VALID = '2345'
    DEFAULT_MISSTYPE_INVALID = 'NaN'
    
    def setUp(self) -> None:
        self.FIELD = Field[self.T]

    def test_prevent_double_initialization(self):
        f = Field[self.T](self.DEFAULT)
        f.__init__(self.DEFAULT_MISSTYPE_VALID)
        self.assertTrue(f.__get_default__() == self.DEFAULT)

    def test_require_default(self):
        self.assertRaises(ValueError, self.FIELD)
        
    def test_default(self):
        self.assertTrue(self.FIELD(self.DEFAULT).__get_default__() == self.DEFAULT, msg='Bad default value')

    def test_default_misstype_valid(self):
        self.assertTrue(self.FIELD(self.DEFAULT_MISSTYPE_VALID).__get_default__() == self.T(self.DEFAULT_MISSTYPE_VALID) , msg='Valid misstype')

    def test_default_misstype_invalid(self):
        self.assertRaises(ValueError, self.FIELD, self.DEFAULT_MISSTYPE_INVALID, msg="Not raised or bad exception")
        
    def test_default_callable(self):
        self.assertTrue(self.FIELD(lambda: self.DEFAULT).__get_default__() == self.DEFAULT, msg='Bad default value')

    def test_default_callable_misstype_valid(self):
        self.assertTrue(self.FIELD(lambda: self.DEFAULT_MISSTYPE_VALID).__get_default__() == self.T(self.DEFAULT_MISSTYPE_VALID) , msg='Valid misstype')

    def test_default_callable_misstype_invalid(self):
        self.assertRaises(ValueError, self.FIELD, lambda: self.DEFAULT_MISSTYPE_INVALID, msg="Not raised or bad exception")

    def test_clone(self):
        f = self.FIELD(self.DEFAULT)
        self.assertFalse(id(f) == id(f.__clone__()))

    def test_clone_new_default(self):
        f = self.FIELD(self.DEFAULT)
        f_clone = f.__new_default__(self.DEFAULT_MISSTYPE_VALID)
        self.assertFalse(f.__get_default__() == f_clone.__get_default__())

    def test_prevent_set(self):
        f = self.FIELD(self.DEFAULT)
        self.assertRaises(TypeError, f.__set__, self.DEFAULT)


class TestStrField(TestIntField):
    T = str
    DEFAULT = 'default'
    DEFAULT_MISSTYPE_VALID = True
    
    class NotStr:
        def __str__(self):
            raise ValueError('can`t cast to str')
    
    DEFAULT_MISSTYPE_INVALID = NotStr()


class TestBoolField(TestIntField):
    T = bool
    DEFAULT = False
    DEFAULT_MISSTYPE_VALID = 1
    
    class NotBool:
        def __bool__(self):
            raise ValueError('can`t cast to bool')
    
    DEFAULT_MISSTYPE_INVALID = NotBool()


class TestFloatField(TestIntField):
    T = float
    DEFAULT = .1
    DEFAULT_MISSTYPE_VALID = int(1)
    DEFAULT_MISSTYPE_INVALID = '0,3'


class TestStrEnumField(TestIntField):
    class StrEnum(Enum):
        SOME = 'SOME'
        NONE = 'NONE'
    T = StrEnum
    DEFAULT = StrEnum.NONE
    DEFAULT_MISSTYPE_VALID = 'SOME'   
    DEFAULT_MISSTYPE_INVALID = 1


class TestIntEnumField(TestIntField):
    class IntEnum(Enum):
        ONE = 1
        TWO = 2
    T = IntEnum
    DEFAULT = IntEnum.ONE
    DEFAULT_MISSTYPE_VALID = 2
    DEFAULT_MISSTYPE_INVALID = 3