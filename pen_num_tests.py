from unittest import TestCase
from fractions import Fraction as Q
import pen_num
from pen_num import RatInterval as RI, Number as Y

class PenNumSanityCheck(TestCase):
  '''Quick way to make sure tests in this module are being run'''
  def test_hello_world(self):
    self.assertEqual(2+2, 4)

  #def test_error(self):
  #  self.assertTrue(False)

class RatIntervalConstructorTests(TestCase):
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

class RatIntervalOpsTests(TestCase):
  pass

class IntervalsForAlphaTest(TestCase):
  def test_intervals_for_alpha(self):
    f = pen_num._generating_poly
    prev = None
    for i, interval in zip(range(40), pen_num._intervals_for_alpha()):
      with self.subTest(iteration = i):
        # Make sure this iteration's interval is a proper subset of the
        # last iteration's:
        if prev is not None:
          self.assertTrue(interval.is_subset_of(prev))
          self.assertLess(interval.width(), prev.width())
        # Make sure we're still bounding the generating polynomial's zero:
        self.assertLess(f(interval.low), 0)
        self.assertGreater(f(interval.high), 0)

      prev = interval

class TestConstants(TestCase):
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
