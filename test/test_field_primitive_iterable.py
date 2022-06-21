from metaconfig import Field
from typing import Tuple
import unittest

class TestPrimitiveIterable(unittest.TestCase):
    F = Field[Tuple[int]]

    def test_no_default(self):
        self.F()

    def test_empty_tuple(self):
        self.assertTupleEqual(self.F().__get_default__(), tuple())

    def test_positional_arg(self):
        self.assertTupleEqual(self.F(1).__get_default__(), (1,))

    def test_iterable_arg(self):
        self.assertTupleEqual(self.F((1,2)).__get_default__(), (1,2))