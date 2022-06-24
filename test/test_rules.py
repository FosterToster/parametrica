import unittest
from typing import Any
from metaconfig.rules import Multirule, Rule, AND, OR
from metaconfig.rules import Min, Max, InRange, MinLen, MaxLen, Match

class TestRules(unittest.TestCase):

    def test_type_check(self):
        class CustomRule(Rule[int]):
            def try_check(self, value: Any) -> Any:
                return value

        CustomRule(1).type_check(int)
        self.assertRaises(TypeError, CustomRule(1).type_check, str)
    
    def test_implicit_call(self):
        class CustomRule(Rule[int]):
            def try_check(self, value: Any) -> Any:
                return value

        self.assertEqual(CustomRule(1)(1), 1)

    def test_min(self):
        Min(3)(3)
        Min(3)(4)
        
        with self.assertRaises(ValueError):
            Min(3)(2)
        
        with self.assertRaises(ValueError):
            Min(3)(-1)
    
    def test_max(self):
        Max(3)(2)
        Max(3)(3)
        
        with self.assertRaises(ValueError):
            Max(3)(4)
    
    def test_inrange(self):
        rule = InRange(0, 3)

        rule(0)
        rule(2)
        rule(3)
        
        with self.assertRaises(ValueError):
            rule(4)
        
        with self.assertRaises(ValueError):
            rule(-1)

    def test_minlen(self):
        rule = MinLen(2)
        rule('ab')
        rule('abc')
        
        with self.assertRaises(ValueError):
            rule('a')

    def test_maxlen(self):
        rule = MaxLen(2)
        rule('a')
            
        rule('ab')
        
        with self.assertRaises(ValueError):
            rule('abc')

    def test_match(self):
        rule = Match(r'^\d{3}$')
        rule('123')
        rule('892')

        with self.assertRaises(ValueError):
            rule('abc')
        
        with self.assertRaises(ValueError):
            rule('12')

    def test_operator_or(self):
        rule = InRange(0,3) | InRange(5, 7)

        self.assertTrue(isinstance(rule, OR))

        with self.assertRaises(ValueError):
            rule(-1)
        
        rule(0)
        rule(1)
        rule(2)
        rule(3)
        
        with self.assertRaises(ValueError):
            rule(4)
        
        rule(5)
        rule(6)
        rule(7)

        with self.assertRaises(ValueError):
            rule(8)
        

    def test_operator_and(self):
        rule = Min(0) + Max(3)

        self.assertTrue(isinstance(rule, AND))

        rule(0)
        rule(2)
        rule(3)
        
        with self.assertRaises(ValueError):
            rule(4)
        
        with self.assertRaises(ValueError):
            rule(-1)

    def test_multirule_typecheck(self):
        rule = Multirule(Min(0), Max(1))
        rule.type_check(int)
        with self.assertRaises(TypeError):
            rule.type_check('hello')


    def text_extend_multirule(self):
        rule = Multirule(Multirule(Min(0), Max(1)),Multirule(Min(0), Max(1)))
        self.assertEqual(len(rule.__rules__), 4)
        
        

        
    