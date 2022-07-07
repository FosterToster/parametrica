
import unittest
from parametrica.rules import Max

from parametrica.types import Fieldset, Field


class TestFieldMethods(unittest.TestCase):

    def setUp(self) -> None:
        self.f = Field[int](3)

    def test_default(self):
        f = self.f.default(2)
        self.assertNotEqual(id(f), id(self.f))
        self.assertNotEqual(f.__get_default__(), self.f.__get_default__())

    def label(self):
        f = self.f.label("label")
        self.assertNotEqual(id(f), id(self.f))
        self.assertNotEqual(self.f.__label__, "label")
        self.assertEqual(f.__label__, "label")

    def hint(self):
        f = self.f.hint("label")
        self.assertNotEqual(id(f), id(self.f))
        self.assertNotEqual(self.f.__hint__, "label")
        self.assertEqual(f.__hint__, "label")

    def secret(self):
        f1 = self.f.secret()
        self.assertNotEqual(id(f1), id(self.f))
        self.assertNotEqual(self.f.__secret__, True)
        self.assertEqual(f1.__secret__, False)
        f2 = f1.secret(False)
        self.assertNotEqual(id(f1), id(f2))
        self.assertEqual(f1.__secret__, True)
        self.assertNotEqual(f2.__secret__, False)

    def secret_set_value(self):
        class Some(Fieldset):
            f = self.f.secret()
        
        instance = Some()
        self.assertTrue(instance.__get_field__('f').__secret__)
        instance.__set_value__({'f': 4})
        self.assertFalse(instance.__get_field__('f').__secret__)

    def rule(self):
        f = self.f.rule(Max(1))
        self.assertNotEqual(id(f), id(self.f))
        self.assertNotEqual(self.f.__rule__, f.__rule__)
        
    def rule_validation(self):
        f = self.f.rule(Max(1))
        f.__normalize_value__(1)

        with self.assertRaises(ValueError):
            f.__normalize_value__(2)