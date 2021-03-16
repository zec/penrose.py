# MIT-licensed; see LICENSE for details

from unittest import TestCase, skip
from fractions import Fraction as Q
import pen_num
from pen_num import RatInterval as RI, Number as Y

class PenNumSanityCheck(TestCase):
  '''Quick way to make sure tests in this module are being run'''
  def test_hello_world(self):
    self.assertEqual(2+2, 4)

  #def test_error(self):
  #  self.assertTrue(False)

class TestRatIntervalConstructor(TestCase):
  def test_pairs_should_succeed(self):
    cases = [
      (Q(5,1),    Q(11,2)),
      (Q(-1,1),   Q(0,1)),
      (Q(-1,2),   Q(1,2)),
      (Q(13,5),   Q(14,5)),
      (Q(12,7),   Q(12,7)),
      (4,         Q(22,5)),
      (-5,        -2),
      (Q(-22,7),  0),
      (-2.5,      Q(0,1)),
      (3,         3),
      (5,         Q(10,2)),
    ]
    for l, h in cases:
      with self.subTest(low = l, high = h):
        interval = RI(l, h)
        self.assertEquals(type(interval.low),  Q)
        self.assertEquals(type(interval.high), Q)
        self.assertEquals(interval.low,  l)
        self.assertEquals(interval.high, h)

  def test_singles_should_succeed(self):
    cases = [
      Q(0,1),
      Q(5,2),
      Q(-14,3),
      Q(1,1_000_000),
      -17,
      22.25,
    ]
    for c in cases:
      with self.subTest(num = c):
        interval = RI(c)
        self.assertEquals(type(interval.low),  Q)
        self.assertEquals(type(interval.high), Q)
        self.assertEquals(interval.low,  c)
        self.assertEquals(interval.high, c)

  def test_pairs_should_not_succeed(self):
    cases = [
      (Q(11,2),    Q(5,1),     ValueError),
      (None,       Q(1,1),     TypeError),
      (Q(5,2),     'no',       ValueError),
      ('xyzzy',    'xyzzy',    ValueError),
      (0,          -20,        ValueError),
    ]
    for l, h, e in cases:
      with self.subTest(low = l, high = h, exception = e):
        self.assertRaises(e, RI, l, h)

  def test_singles_should_not_succeed(self):
    cases = [
      ('bleh',   ValueError),
      (None,     TypeError),
      ((1,2,3),  TypeError),
    ]
    for n, e in cases:
      with self.subTest(num = n, exception = e):
        self.assertRaises(e, RI, n)

class TestRatIntervalOps(TestCase):
  def test_negation(self):
    cases = [
      ([Q(1,1), Q(2,1)],   [Q(-2,1), Q(-1,1)]),
      ([Q(0,1), Q(1,7)],   [Q(-1,7), Q(0,1)]),
      ([Q(-2,1), Q(1,1)],  [Q(-1,1), Q(2,1)]),
      ([Q(-2,5), Q(0,1)],  [Q(0,1), Q(2,5)]),
      ([Q(-8,7), Q(-1,5)], [Q(1,5), Q(8,7)]),
    ]
    for x, y in cases:
      with self.subTest(num = x):
        self.assertEquals(-(RI(*x)), RI(*y))

  def test_addition(self):
    cases = [
      (RI(0, 1),             RI(Q(1,3), Q(3,7)),    RI(Q(1,3), Q(10,7))),
      (RI(Q(0,1), Q(2,3)),   RI(Q(0,1), Q(1,5)),    RI(Q(0,1), Q(13,15))),
      (RI(Q(-22,5), Q(4,3)), RI(1, 2),              RI(Q(-17,5), Q(10,3))),
      (RI(-4, Q(-2,3)),      RI(Q(-2,5), Q(-1,5)),  RI(Q(-22,5), Q(-13,15))),
      (RI(-3, 2),            Q(1,5),                RI(Q(-14,5), Q(11,5))),
      (-4,                   RI(1, 3),              RI(-3, -1)),
      (0,                    RI(5, 7),              RI(5, 7)),
      (RI(Q(4,5), 1),        0,                     RI(Q(4,5), 1)),
    ]
    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEquals(a + b, c)

  def test_subtraction(self):
    cases = [
      (RI(Q(1,2), Q(2,3)),   RI(Q(1,7), Q(1,5)),  RI(Q(3,10), Q(11,21))),
      (RI(3, 5),             RI(-4, Q(-7, 2)),    RI(Q(13,2), Q(9,1))),
      (RI(-4, -2),           RI(-4, -2),          RI(-2, 2)),
      (RI(2, 3),             3,                   RI(-1, 0)),
      (15,                   RI(Q(1,2), 1),       RI(14, Q(29,2))),
      (Q(-2,7),              RI(Q(1,7), Q(4,7)),  RI(Q(-6,7), Q(-3,7))),
    ]
    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEquals(a - b, c)

  def test_multiplication(self):
    cases = [
      (RI(Q(1,2), Q(3,5)),    RI(Q(4,7), Q(100,9)),    RI(Q(2,7), Q(20,3))),
      (RI(Q(0,1), Q(1,2)),    RI(Q(-5,1), Q(-9,2)),    RI(Q(-5,2), Q(0,1))),
      (RI(-1, 2),             RI(Q(-1,2), Q(3,5)),     RI(-1, Q(6,5))),
      (RI(-2, 0),             RI(Q(1,5), Q(1,3)),      RI(Q(-2,3), 0)),
      (RI(3, 5),              -2,                      RI(-10, -6)),
      (3,                     RI(5, 7),                RI(15, 21)),
    ]
    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEquals(a * b, c)

class TestIntervalsForAlpha(TestCase):
  def test_intervals_for_alpha(self):
    f = pen_num._generating_poly
    prev = None
    for i, interval in zip(range(40), pen_num._intervals_for_alpha()):
      with self.subTest(iteration = i):
        self.assertEquals(type(interval),  RI)
        # Make sure this iteration's interval is a proper subset of the
        # last iteration's:
        if prev is not None:
          self.assertTrue(interval.is_subset_of(prev))
          self.assertLess(interval.width(), prev.width())
        # Make sure we're still bounding the generating polynomial's zero:
        self.assertLess(f(interval.low), 0)
        self.assertGreater(f(interval.high), 0)

      prev = interval

class TestNumberProperties(TestCase):
  def test_constructor_succeed(self):
    cases = [
      ([],                 (Q(0),    Q(0),   Q(0), Q(0))),
      ([0],                (Q(0),    Q(0),   Q(0), Q(0))),
      ([3],                (Q(3),    Q(0),   Q(0), Q(0))),
      ([Q(-1,7)],          (Q(-1,7), Q(0),   Q(0), Q(0))),

      ([0, '1/2'],         (Q(0),    Q(1,2), Q(0), Q(0))),
      ([2, 3, 5, 8],       (Q(2),    Q(3),   Q(5), Q(8))),
      ([Q(1,2), 0, 0, -2], (Q(1,2),  Q(0),   Q(0), Q(-2))),
    ]
    for args, vec in cases:
      with self.subTest(args = args):
        num_vec = Y(*args)._vec
        self.assertEqual(len(num_vec), 4)
        self.assertTrue(all(type(q) == Q for q in num_vec))
        self.assertTrue(all(
          (a.numerator == b.numerator and a.denominator == b.denominator)
          for a, b in zip(num_vec, vec)
        ))

  def test_constructor_fail(self):
    cases = [
      ([None],             TypeError),
      ([1,2,3,4,5],        TypeError),
      ([0, 0, 'xyzzy', 2], ValueError),
      ([Q(1,2), (3,4)],    TypeError),
    ]
    for args, exception in cases:
      with self.subTest(args = args):
        self.assertRaises(exception, Y, *args)

  def test_bool(self):
    cases = [
      (Y(0, 0, 0, 0),            False),
      (Y(1, 0, 0, 0),            True),
      (Y(0, -1, 0, 0),           True),
      (Y(0, 0, 0, 42),           True),
      (Y(Q(1,10000), 0, 0, 0),   True),
      (Y(Q(-1,10000), 0, 0, 0),  True),
      (Y(Q(-864,227), 1, 0, 0),  True),
      (Y(Q(-863,227), 1, 0, 0),  True),
    ]
    for x, y in cases:
      with self.subTest(num = x):
        self.assertEqual(bool(x), y)

  def test_float(self):
    cases = [
      (Y(0, 0, 0, 0),        -1e-10,      1e-10),
      (Y(1, 0, 0, 0),      0.999999,   1.000001),
      (Y(0, 1, 0, 0),      3.804226,   3.804227),
      (Y(0, 0, 1, 0),     14.472135,  14.472136),
      (Y(0, 0, 0, 1),     55.055276,  55.055277),

      (Y('2/3', 0, 0, 0),  0.666666,   0.666667),
      (Y('5/2', 0, 0, 0),  2.499999,   2.500001),
      (Y(-14, 0, 0, 0),  -14.000001, -13.999999),

      (pen_num.phi,        1.618033,   1.618034),
      (Y(0, '1/4', 0, 0),  0.951056,   0.951057),
      (Y('-3/2', 0, '1/8', 0),
                           0.309016,   0.309017),
    ]
    for x, y, z in cases:
      with self.subTest(num = x):
        f = float(x)
        self.assertEqual(type(f), float)
        self.assertLess(y, f)
        self.assertLess(f, z)

  def test_is_rational(self):
    cases = [
      (Y(0, 0, 0, 0),            True),
      (Y(1, 0, 0, 0),            True),
      (Y(0, -1, 0, 0),           False),
      (Y(0, 0, 0, 42),           False),
      (Y(Q(1,10000), 0, 0, 0),   True),
      (Y(Q(-1,10000), 0, 0, 0),  True),
      (Y(Q(-864,227), 1, 0, 0),  False),
      (Y(Q(-863,227), 1, 0, 0),  False),
    ]
    for x, y in cases:
      with self.subTest(num = x):
        self.assertEqual(x.is_rational(), y)

class TestNumberOps(TestCase):
  def test_interval_sequence(self):
    cases = [
      Y(0, 0, 0, 0),
      Y(1, 0, 0, 0),
      Y(0, -1, 0, 0),
      Y(0, 0, 0, 42),
      Y(Q(1,10000), 0, 0, 0),
      Y(Q(-1,10000), 0, 0, 0),
      Y(Q(-864,227), 1, 0, 0),
      Y(Q(-863,227), 1, 0, 0),
    ]
    for x in cases:
      with self.subTest(num = x):
        last_interval = None
        for i, interval in zip(range(40), x.interval_sequence()):
          self.assertEqual(type(interval), RI)

          if x.is_rational():
            self.assertEqual(interval.width(), 0)
          elif last_interval is not None:
            self.assertTrue(interval.is_subset_of(last_interval))
            self.assertLess(interval.width(), last_interval.width())

          last_interval = interval

  def test_sgn(self):
    cases = [
      (Y(0, 0, 0, 0),            0),
      (Y(1, 0, 0, 0),           +1),
      (Y(0, 1, 0, 0),           +1),
      (Y(0, 0, 1, 0),           +1),
      (Y(0, 0, 0, 1),           +1),

      (Y('2/3', 0, 0, 0),       +1),
      (Y('5/2', 0, 0, 0),       +1),
      (Y(-14, 0, 0, 0),         -1),

      (pen_num.phi,             +1),
      (Y(0, '1/4', 0, 0),       +1),
      (Y('-3/2', 0, '1/8', 0),  +1),

      (Y(Q(-863,227), 1, 0, 0), +1), # alpha is between 863/227 and 864/227
      (Y(Q(-864,227), 1, 0, 0), -1),
    ]
    for x, y in cases:
      with self.subTest(num = x):
        self.assertEqual(x.sgn(), y)
        self.assertEqual((-x).sgn(), -y)

  def test_floor_ceil_int(self):
    from math import floor, ceil

    cases = [
      (Y(0, 0, 0, 0),  0,  0,  0),
      (Y(1, 0, 0, 0),  1,  1,  1),
      (Y(0, 1, 0, 0),  3,  4,  3),
      (Y(0, 0, 1, 0), 14, 15, 14),
      (Y(0, 0, 0, 1), 55, 56, 55),

      (Y('2/3', 0, 0, 0),  0,   1,   0),
      (Y('5/2', 0, 0, 0),  2,   3,   2),
      (Y(-14, 0, 0, 0),  -14, -14, -14),

      (Y(0, -1, 0, 0),           -4,   -3,   -3),
      (Y(0, 0, '-1/2', 0),       -8,   -7,   -7),
      (Y(0, 0, 0, 42),         2312, 2313, 2312),
      (Y(Q(1,10000), 0, 0, 0),    0,    1,    0),
      (Y(Q(-1,10000), 0, 0, 0),  -1,    0,    0),

      (Y(0, 0, 0, '1/100'),    0, 1, 0),
      (Y(0, 0, 0, '-1/100'),  -1, 0, 0),

      (pen_num.phi,            1, 2, 1),
      (Y(0, '1/4', 0, 0),      0, 1, 0),
      (Y('-3/2', 0, '1/8', 0), 0, 1, 0),

      (Y(Q(-863,227), 1, 0, 0),  0, 1, 0),
      (Y(Q(-864,227), 1, 0, 0), -1, 0, 0),
    ]
    for x, f, c, i in cases:
      with self.subTest(num = x):
        self.assertEqual(floor(x), f)
        self.assertEqual(ceil(x),  c)
        self.assertEqual(int(x),   i)

  def test_comparisons(self):
    T, F = True, False
    cases = [
      # lt le eq ne ge gt
      (Y(0), Y(0),
         F, T, T, F, T, F),
      (Y('1/2'), Y(2),
         T, T, F, T, F, F),
      (Q(863, 227), Y(0, 1),
         T, T, F, T, F, F),
      (Q(864, 227), Y(0, 1),
         F, F, F, T, T, T),
      (Y(0, 0, 0, 1), 55,
         F, F, F, T, T, T),
      (Y(0, 12, 0, 4), Y(0, 12, 0, 4),
         F, T, T, F, T, F),
      (Q(265.87), Y(0, 12, 0, 4),
         T, T, F, T, F, F),
      (Q(265.88), Y(0, 12, 0, 4),
         F, F, F, T, T, T),
    ]
    for a, b, lt, le, eq, ne, ge, gt in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a < b,  lt)
        self.assertEqual(b > a,  lt)
        self.assertEqual(a <= b, le)
        self.assertEqual(b >= a, le)

        self.assertEqual(a == b, eq)
        self.assertEqual(b == a, eq)
        self.assertEqual(a != b, ne)
        self.assertEqual(b != a, ne)

        self.assertEqual(a >= b, ge)
        self.assertEqual(b <= a, ge)
        self.assertEqual(a > b,  gt)
        self.assertEqual(b < a,  gt)

  def test_negation(self):
    cases = [
      (Y(2, 3, 4, 5),     Y(-2, -3, -4, -5)),
      (Y(0, 0, 0, 0),     Y(0, 0, 0, 0)),
      (Y(1, 0, 0, 0),     Y(-1, 0, 0, 0)),
      (Y(0, 1, 0, 0),     Y(0, -1, 0, 0)),
      (Y(0, 0, 1, 0),     Y(0, 0, -1, 0)),
      (Y(0, 0, 0, 1),     Y(0, 0, 0, -1)),
      (Y('-863/227', 1),  Y('863/227', -1)),
      (Y('864/227', -1),  Y('-864/227', 1)),
    ]
    for x, y in cases:
      with self.subTest(num = x):
        self.assertEqual(-x, y)
        self.assertEqual(x, -y)

  def test_addition(self):
    cases = [
      (Y(0),               Y(0),         Y(0)),
      (Y(1),               Y(0),         Y(1)),
      (Y(2),               Y(2),         Y(4)),
      (Y('1/4'),           Y('-1/4'),    Y(0)),
      (Y(Q(12,7)),         Y(0, 1),      Y(Q(12,7), 1, 0, 0)),
      (Y(2, '-1/5', 0, 1), Y(-2, 0, -2), Y(0, '-1/5', -2, 1)),
      (Y(3, 0, '3/11', 0), 4,            Y(7, 0, '3/11', 0)),
      (Q(-23,2),           Y(1, 1),      Y(Q(-21,2), 1)),
    ]
    zero = Y(0)

    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a + b, c)
        self.assertEqual(b + a, c)
        self.assertEqual(a + zero, a)
        self.assertEqual(b + zero, b)

  def test_subtraction(self):
    cases = [
      (Y(0),               Y(0),           Y(0)),
      (Y(Q(1,2), 0, 0, 0), Y(0, 3, 0, 0),  Y('1/2', -3, 0, 0)),
      (31,                 Y(32, 0, 4, 0), Y(-1, 0, -4, 0)),
      (Y(0, 0, 0, -3),     Q(-15,4),       Y(Q(15,4), 0, 0, -3)),
    ]
    zero = Y(0)
    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a - b, c)
        self.assertEqual(b - a, -c)
        self.assertEqual(a - zero, a)
        self.assertEqual(b - zero, b)
        self.assertEqual(zero - a, -a)
        self.assertEqual(zero - b, -b)

  def test_multiplication(self):
    cases = [
      (Y(1, 0, 0, 0), Y(1, 0, 0, 0), Y(1, 0, 0, 0)),
      (Y(1, 0, 0, 0), Y(0, 1, 0, 0), Y(0, 1, 0, 0)),
      (Y(1, 0, 0, 0), Y(0, 0, 1, 0), Y(0, 0, 1, 0)),
      (Y(1, 0, 0, 0), Y(0, 0, 0, 1), Y(0, 0, 0, 1)),
      (Y(0, 1, 0, 0), Y(0, 1, 0, 0), Y(0, 0, 1, 0)),
      (Y(0, 1, 0, 0), Y(0, 0, 1, 0), Y(0, 0, 0, 1)),
      (Y(0, 1, 0, 0), Y(0, 0, 0, 1), Y(-80, 0, 20, 0)),
      (Y(0, 0, 1, 0), Y(0, 0, 1, 0), Y(-80, 0, 20, 0)),
      (Y(0, 0, 1, 0), Y(0, 0, 0, 1), Y(0, -80, 0, 20)),
      (Y(0, 0, 0, 1), Y(0, 0, 0, 1), Y(-1600, 0, 320, 0)),

      (Y(2, 0, 3, 0),  Y(0, 5, 0, 0), Y(0, 10, 0, 15)),
      (Y(2, 0, 0, -3), Y(0, 5, 0, 0), Y(1200, 10, -300, 0)),

      (Q(-5,3),       Y(0, 2, 2, 0), Y(0, '-10/3', '-10/3', 0)),
      (Y(0, 0, 42),   2,             Y(0, 0, 84)),
    ]
    one  = Y(1)
    zero = Y(0)

    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a * b, c)
        self.assertEqual(b * a, c)
        self.assertEqual(a * one, a)
        self.assertEqual(b * one, b)
        self.assertEqual(a * zero, zero)
        self.assertEqual(b * zero, zero)

class TestConstants(TestCase):
  '''Some sanity checks of Number and the constants defined in pen_num'''

  def test_one(self):
    # it *is* the integer 1, right?
    self.assertEquals(pen_num.one, 1)

  def test_phi(self):
    phi = pen_num.phi
    # 1/phi == phi - 1
    self.assertEquals(phi * (phi - 1), 1)
    # phi^2 == phi + 1
    self.assertEquals(phi * phi, phi + 1)
    # phi > 1
    self.assertGreater(phi, 1)
    # inv_phi = 1/phi
    self.assertEquals(phi * pen_num.inv_phi, 1)

  def test_sqrt5(self):
    sqrt5 = pen_num.sqrt5
    # 13/6 < sqrt5 < 9/4
    self.assertLess(Q(13,6), sqrt5)
    self.assertLess(sqrt5,   Q(9,4))
    # sqrt5^2 == 5
    self.assertEquals(sqrt5 * sqrt5, 5)

  def test_alpha_manual_powers(self):
    alpha = pen_num.alpha
    self.assertEquals(alpha, Y(0, 1, 0, 0))
    self.assertEquals(alpha*alpha, Y(0, 0, 1, 0))
    self.assertEquals(alpha*alpha*alpha, Y(0, 0, 0, 1))
    self.assertEquals(alpha*alpha*alpha*alpha, Y(-80, 0, 20, 0))
    self.assertEquals(alpha*alpha*alpha*alpha*alpha, Y(0, -80, 0, 20))
