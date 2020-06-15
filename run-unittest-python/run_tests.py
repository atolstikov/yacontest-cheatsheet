#!/usr/bin/env python
# coding: utf-8

import sys
import io

import unittest

import expression


class TestExpression(unittest.TestCase):
    def test_addition(self):
        self.assertEqual(expression.evaluate_expression("1+1"), 2)
        self.assertEqual(expression.evaluate_expression("1+0"), 1)
        self.assertEqual(expression.evaluate_expression("0+0"), 0)
        self.assertEqual(expression.evaluate_expression("2+2"), 4)

    def test_subtraction(self):
        self.assertEqual(expression.evaluate_expression("1-1"), 0)
        self.assertEqual(expression.evaluate_expression("1-0"), 1)
        self.assertEqual(expression.evaluate_expression("0-0"), 0)
        self.assertEqual(expression.evaluate_expression("0-2"), -2)

    def test_multiplication(self):
        self.assertEqual(expression.evaluate_expression("1*1"), 1)
        self.assertEqual(expression.evaluate_expression("1*0"), 0)
        self.assertEqual(expression.evaluate_expression("0*0"), 0)
        self.assertEqual(expression.evaluate_expression("2*2"), 4)

    def test_division(self):
        self.assertEqual(expression.evaluate_expression("1/1"), 1.0)
        self.assertRaises(ZeroDivisionError, expression.evaluate_expression, "1/0")
        self.assertRaises(ZeroDivisionError, expression.evaluate_expression, "0/0")
        self.assertEqual(expression.evaluate_expression("0/2"), 0.0)


def get_score(log):
    scores = []
    test_scores = {
        'test_addition': 1.0,
        'test_subtraction': 1.0,
        'test_multiplication': 1.0,
        'test_division': 2.0,
    }
    for line in log.strip().split('\n'):
        line = line.strip().split()
        if not line:
            continue
        if line[-1] == 'ok':
            scores.append(test_scores[line[0]])
    return sum(scores)


suite = unittest.TestLoader().loadTestsFromTestCase(TestExpression)
string_io = io.StringIO()
unittest.TextTestRunner(verbosity=2, stream=string_io).run(suite)
scored_result = get_score(string_io.getvalue())

print(string_io.getvalue(), file=sys.stderr)
print("Score ", scored_result)
