from unittest import TestCase, skip
import pen_geom as g
from fractions import Fraction as Q
from pen_num import Number as Y, phi, inv_phi, sqrt5, alpha
from itertools import zip_longest

class PenGeomSanityCheck(TestCase):
  '''Quick way to make sure tests in this module are being run'''
  def test_hello_world(self):
    self.assertEqual(2+2, 4)

  #def test_error(self):
  #  self.assertTrue(False)

class TestPoint(TestCase):
  def test_point_constructor_succeed(self):
    cases = [
      ( (Y(0), Y(0)),             Y(0, 0, 0, 0),        Y(0, 0, 0, 0) ),
      ( (Y(1), Y(-4)),            Y(1, 0, 0, 0),        Y(-4, 0, 0, 0) ),
      ( (Y(0,2,0,0), Y(0,0,0,1)), Y(0, 2, 0, 0),        Y(0, 0, 0, 1) ),
      ( (Q(-1,3), Q(4, 3)),       Y(Q(-1,3), 0, 0, 0),  Y(Q(4,3), 0, 0, 0) ),
      ( (5, 0),                   Y(5, 0, 0, 0),        Y(0, 0, 0, 0) ),
      ( (g.Point(5, 0),),         Y(5, 0, 0, 0),        Y(0, 0, 0, 0) ),
      ( ('1/2', 2),               Y(Q(1,2), 0, 0, 0),   Y(2, 0, 0, 0) ),
    ]
    for args, x, y in cases:
      with self.subTest(args = args):
        pt = g.Point(*args)
        self.assertEqual(type(pt), g.Point)
        self.assertEqual(pt.x, x)
        self.assertEqual(pt.y, y)

  def test_point_constructor_fail(self):
    cases = [
      ( (),                   TypeError ),
      ( ((), ()),             TypeError ),
      ( (Y(42),),             TypeError ),
      ( (Y(14), False),       TypeError ),
      ( (g.Point(1,1), 0),    TypeError ),
      ( (g.Vector(1,1),),     TypeError ),
      ( ('lkaskfdj',),        TypeError ),
      ( ('bleh', True),       TypeError ),
      ( ('xyzzy', 'plugh'),   TypeError ),
    ]
    for args, ex in cases:
      with self.subTest(args = args):
        self.assertRaises(ex, g.Point, *args)

  def test_point_equality_and_hash(self):
    P = g.Point
    cases = [
      (0,  P(3, 4),              P(Y(3,0,0,0), Y(4,0,0,0)),   True),
      (1,  P(Y(0,1), 1),         P(Y(0,1,0,0), Y(1,0,0,0)),   True),
      (2,  P(3, 5),              P(3, 4),                     False),
      (3,  P(Y('-864/227',1),0), P(Y('-863/227',1),0),        False),
      (4,  P(Y('-864/227',1),0), P(0, 0),                     False),
      (5,  P(2, 3),              P(3, 2),                     False),
      (6,  P('32/4', -2),        P(8, '-2'),                  True),
      (7,  P(1, 1),              P(1, 1),                     True),
      (8,  P(phi, -phi),         P(phi, -phi),                True),
      (9,  P(-phi, phi),         P(-phi, phi),                True),
      (10, P(phi, -phi),         P(-phi, phi),                False),
      (11, P(phi, phi),          P(-phi, -phi),               False),
      (12, P(1, 0),              g.Vector(1, 0),              False),
    ]
    for i, a, b, result in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a == b, result)
        self.assertEqual(b == a, result)
        self.assertEqual(a != b, not result)
        self.assertEqual(b != a, not result)
        self.assertTrue(a == a)
        self.assertTrue(b == b)
        if result:
          self.assertEqual(hash(a), hash(b))

  def test_transform(self):
    P, AT, ident = g.Point, g.AffineTransform, g.identity_transform
    T, R, S      = g.translation, g.rotation, g.scaling
    cases = [
      (0,  P(0, 0),     ident,            P(0, 0)),
      (1,  P(phi, 1),   ident,            P(phi, 1)),
      (2,  P(2, -3),    ident,            P(2, -3)),
      (3,  P(0, 0),     AT(0,2,3, 3,0,1), P(3, 1)),
      (4,  P(1, 0),     AT(0,2,3, 3,0,1), P(3, 4)),
      (5,  P(0, 1),     AT(0,2,3, 3,0,1), P(5, 1)),
      (6,  P(1, 1),     R(5),             P(-1, 1)),
      (7,  P(5, 4),     R(-5) @ T(1,1),   P(5, -6)),
      (8,  P(-1, -1),   S(phi),           P(-phi, -phi)),
    ]
    for i, pt, trans, result in cases:
      with self.subTest(i = i, pt = pt, trans = trans):
        self.assertEqual(pt.transform(trans), result)
        self.assertEqual(trans @ pt, result)

  def test_subtraction_succeed(self):
    P, V = g.Point, g.Vector
    cases = [
      (0,  P(2, 3),     P(0, 0),       V(2, 3)),
      (1,  P(25, -9),   P(2, -sqrt5),  V(23, -9 + sqrt5)),
      (2,  P(35, 2),    P(23, 24),     V(12, -22)),
    ]
    for i, a, b, c in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a - b, c)
        self.assertEqual(b - a, -c)

  def test_subtraction_fail(self):
    P, AT = g.Point, g.AffineTransform
    cases = [
      (0,  P(0, 0),      Y(0),            TypeError),
      (1,  P(35, 0),     AT(1,1,1,2,2,2), TypeError),
      (2,  P(25, -24),   'hello, world',  TypeError),
      (3,  Q(25),        P(0, 0),         TypeError),
    ]
    for i, a, b, ex in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertRaises(ex, (lambda x, y: x - y), a, b)

  def test_addition_succeed(self):
    P, V = g.Point, g.Vector
    cases = [
      (0,  P(0, 0),          V(0, 0),     P(0, 0)),
      (1,  P(0, 0),          V(254, -3),  P(254, -3)),
      (2,  P(14, phi),       V(-14, 0),   P(0, phi)),
      (3,  P(Y(0,1),Q(1,3)), V(2, 3),     P(Y(2,1), Y(Q(10,3)))),
    ]
    for i, a, b, c in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a + b, c)
        self.assertEqual(b + a, c)

  def test_addition_fail(self):
    P = g.Point
    cases = [
      (0,  P(0, 0),       P(0, 0),       TypeError),
      (1,  P(15, 2),      P(-15, -2),    TypeError),
      (2,  P(20, 2),      Y(-23),        TypeError),
      (3,  P(3, -3),      False,         TypeError),
    ]
    for i, a, b, ex in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertRaises(ex, (lambda x, y: x + y), a, b)
        self.assertRaises(ex, (lambda x, y: x + y), b, a)

  def test_translate(self):
    P, V = g.Point, g.Vector
    cases = [
      (0,  P(0, 0),     (0, 0),         P(0, 0)),
      (1,  P(0, 0),     (phi, -sqrt5),  P(phi, -sqrt5)),
      (2,  P(-4, 2),    (1, 1),         P(-3, 3)),
      (3,  P(23, 2),    (V(2, 4),),     P(25, 6)),
    ]
    for i, pt, args, result in cases:
      with self.subTest(i = i, pt = pt, args = args):
        self.assertEqual(pt.translate(*args), result)

  def test_translate_fail(self):
    P, V, R = g.Point, g.Vector, g.rotation
    cases = [
      (0,  P(0, 0),    (0,),             TypeError),
      (1,  P(2, 3),    (0,),             TypeError),
      (2,  P(-3, 2),   (Y(23),),         TypeError),
      (3,  P(1, 1),    (R(7), 2),        TypeError),
      (4,  P(5, 6),    (V(1,1), V(0,0)), TypeError),
      (5,  P(2, 43),   (4, '1/q'),       ValueError),
      (6,  P(2, 4),    (V(2,3), 555),    TypeError),
      (7,  P(23, 4),   (),               TypeError),
    ]
    for i, pt, args, ex in cases:
      with self.subTest(i = i, pt = pt, args = args):
        self.assertRaises(ex, (lambda p, a: p.translate(*a)), pt, args)

  def test_rotate(self):
    P = g.Point
    cases = [
      (0,  P(0, 0),    0,     P(0, 0)),
      (1,  P(0, 0),    4,     P(0, 0)),
      (2,  P(1, 0),    0,     P(1, 0)),
      (3,  P(1, 0),    5,     P(0, 1)),
      (4,  P(1, 0),    10,    P(-1, 0)),
      (5,  P(1, 0),    15,    P(0, -1)),
      (6,  P(1, 0),    20,    P(1, 0)),
      (7,  P(0, 1),    0,     P(0, 1)),
      (8,  P(0, 1),    5,     P(-1, 0)),
      (9,  P(0, 1),    10,    P(0, -1)),
      (10, P(0, 1),    15,    P(1, 0)),
      (11, P(0, 1),    20,    P(0, 1)),
      (12, P(0, 1),    45,    P(-1, 0)),
      (13, P(0, 1),    -15,   P(-1, 0)),
      (14, P(4, 0),    1,     P(Y(0,1), Y(-6,0,Q(1,2)))),
    ]
    for i, pt, theta, result in cases:
      with self.subTest(i = i, pt = pt, theta = theta):
        self.assertEqual(pt.rotate(theta), result)

  def test_bbox(self):
    cases = [
      (0,  0,   0),
      (1,  23,  4),
      (2,  -23, -234),
      (3,  phi, -sqrt5),
    ]
    for i, x, y in cases:
      with self.subTest(i = i, x = x, y = y):
        self.assertEqual(g.Point(x, y).bbox(), g.Rectangle(x, y, x, y))

  def test_as_offset_vector(self):
    P, V = g.Point, g.Vector
    cases = [
      (P(0, 0),     V(0, 0)),
      (P(1, 0),     V(1, 0)),
      (P(0, 1),     V(0, 1)),
      (P(31,'1/2'), V(31,Q(1,2))),
      (P(-5, phi),  V(-5, phi))
    ]
    for pt, vec in cases:
      with self.subTest(pt = pt):
        self.assertEqual(pt.as_offset_vector(), vec)

class TestVector(TestCase):
  def test_vector_constructor_succeed(self):
    cases = [
      (0,  (Y(0), Y(0)),       Y(0,0,0,0),      Y(0,0,0,0)),
      (1,  (0, 0),             Y(0,0,0,0),      Y(0,0,0,0)),
      (2,  (14, -2),           Y(14,0,0,0),     Y(-2,0,0,0)),
      (3,  (Q(1,4),Q(3,7)),    Y(Q(1,4),0,0,0), Y(Q(3,7),0,0,0)),
      (4,  (Y(0,1),3),         Y(0,1,0,0),      Y(3,0,0,0)),
      (5,  (g.Vector(14,-2),), Y(14,0,0,0),     Y(-2,0,0,0)),
      (6,  (g.Point(3,5),),    Y(3,0,0,0),      Y(5,0,0,0)),
    ]
    for i, args, x, y in cases:
      with self.subTest(i = i, args = args):
        v = g.Vector(*args)
        self.assertEqual(type(v), g.Vector)
        self.assertEqual(v.x, x)
        self.assertEqual(v.y, y)

  def test_vector_constructor_fail(self):
    V, P = g.Vector, g.Point
    cases = [
      (0,  (),                TypeError),
      (1,  (Y(3),),           TypeError),
      (2,  (V(0,0), V(0,0)),  TypeError),
      (3,  (P(3,1), P(2,-1)), TypeError),
      (4,  (V(3,2), P(1,1)),  TypeError),
      (5,  (V(21,45), Y(2)),  TypeError),
    ]
    for i, args, ex in cases:
      with self.subTest(i = i, args = args):
        self.assertRaises(ex, g.Vector, *args)

  def test_vector_equality_and_hash(self):
    V = g.Vector
    cases = [
      (0,  V(0, 0),                V(0, 0),          True),
      (1,  V(Y(0,1), Y('1/2')),    V(Y(0,1),Q(1,2)), True),
      (2,  V(2, 3),                V(3, 2),          False),
      (3,  V(2, -3),               V(2, 3),          False),
      (4,  V(14, 4),               g.Point(14, 4),   False),

      (5,  V(Y(Q(-864,227),1),-2), V(0, -2),         False),
      (6,  V(2, 3),                V(-2, -3),        False),
      (7,  V(1, phi + 1),          V(1, phi + 1),    True),
    ]
    for i, a, b, result in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a == b, result)
        self.assertEqual(b == a, result)
        self.assertTrue(a == a)
        self.assertTrue(b == b)
        if result:
          self.assertEqual(hash(a), hash(b))

  def test_negation(self):
    V = g.Vector
    cases = [
      (0,  V(0, 0),        V(0, 0)),
      (1,  V(1, 0),        V(-1, 0)),
      (2,  V(0, 1),        V(0, -1)),
      (3,  V(13, sqrt5+1), V(-13, -1-sqrt5)),
      (4,  V(5, -2),       V(-5, 2)),

      (5,  V(-1, -1),      V(1, 1)),
    ]
    for i, v, r in cases:
      with self.subTest(i = i, vec = v):
        self.assertEqual(-v, r)
        self.assertEqual(v, -r)

  def test_addition(self):
    V = g.Vector
    cases = [
      (0,  V(0, 0),      V(0, 0),       V(0, 0)),
      (1,  V(1, 0),      V(0, 1),       V(1, 1)),
      (2,  V(Q(1,2),-4), V(-2, Q(1,3)), V(Q(-3,2), Q(-11,3))),
      (3,  V(-5, 2),     V(5, -2),      V(0, 0)),
      (4,  V(phi, 2),    V(-1, -1),     V(inv_phi, 1)),
    ]
    zero = g.Vector(0, 0)
    for i, a, b, r in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a + b, r)
        self.assertEqual(b + a, r)
        self.assertEqual(a + zero, a)
        self.assertEqual(b + zero, b)
        self.assertEqual(zero + a, a)
        self.assertEqual(zero + b, b)

  def test_subtraction(self):
    V = g.Vector
    cases = [
      (0,  V(5, 3),     V(0, 0),        V(5, 3)),
      (1,  V(0, 0),     V(0, 0),        V(0, 0)),
      (2,  V(3, 2),     V(55, Q(10,3)), V(-52, Q(-4,3))),
      (3,  V(0, 0),     V(1, 0),        V(-1, 0)),
      (4,  V(45, -3),   V(45, -3),      V(0, 0)),
    ]
    zero = g.Vector(0, 0)
    for i, a, b, r in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a - b, r)
        self.assertEqual(b - a, -r)
        self.assertEqual(a - zero, a)
        self.assertEqual(b - zero, b)
        self.assertEqual(zero - a, -a)
        self.assertEqual(zero - b, -b)
    with self.subTest(i = 999):
      self.assertEqual(g.Point(5, 7) - V(2, 2), g.Point(3, 5))

  def test_scalar_multiplication(self):
    V = g.Vector
    cases = [
      (0,  1,      V(3, -4),         V(3, -4)),
      (1,  phi,    V(Q(1,2), -2),    V(Q(1,2)*phi, -2*phi)),
      (2,  Q(3,4), V(4, 15),         V(3, Q(45,4))),
      (3,  35,     V(0, 0),          V(0, 0)),
      (4,  0,      V(5*sqrt5, 33),   V(0, 0)),
    ]
    zero = g.Vector(0, 0)
    for i, a, b, r in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a * b, r)
        self.assertEqual(b * a, r)
        self.assertEqual(0 * b, zero)
        self.assertEqual(1 * b, b)

  def test_transform(self):
    V, AT = g.Vector, g.AffineTransform
    T, R, S = g.translation, g.rotation, g.scaling
    cases = [
      (0,  V(35, phi - sqrt5),   g.identity_transform,     V(35, phi-sqrt5)),
      (1,  V(0, 0),              T(4, Q(1,2)),             V(0, 0)),
      (2,  V(3, 4),              T(4, Q(1,2)),             V(3, 4)),
      (3,  V(3, 4),              S(3, -5),                 V(9, -20)),
      (4,  V(-4, 5),             AT(3,8,11, 7,-5,-1000),   V(28, -53)),

      (5,  V(1, 1),              R(5),                     V(-1, 1)),
      (6,  V(1, 2),              R(15),                    V(2, -1)),
    ]
    for i, vec, trans, r in cases:
      with self.subTest(i = i, vec = vec, trans = trans):
        self.assertEqual(vec.transform(trans), r)
        self.assertEqual(trans @ vec, r)

  def test_rotate(self):
    V = g.Vector
    cases = [
      (0,  V(0, 0),        3,   V(0, 0)),
      (1,  V(0, 0),        -14, V(0, 0)),
      (2,  V(phi, Q(1,2)), -5,  V(Q(1,2), -phi)),
      (3,  V(1, 0),        10,  V(-1, 0)),
      (4,  V(4, 4),        -1,  V(Y(-6,1,Q(1,2),0),Y(6,1,Q(-1,2),0))),
    ]
    for i, vec, theta, result in cases:
      with self.subTest(i = i, vec = vec, theta = theta):
        self.assertEqual(vec.rotate(theta), result)

  def test_inner_product(self):
    V = g.Vector
    cases = [
      (0,  V(0, 0),        V(5, 2),        Y(0)),
      (1,  V(1, 0),        V(1, 0),        1),
      (2,  V(1, 0),        V(0, 1),        0),
      (3,  V(1, 2),        V(-2, 3),       4),
      (4,  V(phi, 0),      V(-inv_phi, 0), -1),

      (5,  V(33, 14),      V(1, Q(-1,2)),  26),
    ]
    zero = g.Vector(0, 0)
    for i, a, b, r in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a | b, r)
        self.assertEqual(b | a, r)
        self.assertEqual((-a) | b, -r)
        self.assertEqual(a | (-b), -r)
        self.assertEqual((3*a) | b, 3*r)
        self.assertEqual(a | zero, 0)
        self.assertEqual(b | zero, 0)

  def test_cross_product(self):
    V = g.Vector
    cases = [
      (0,  V(0, 0),    V(0, 0),    0),
      (1,  V(1, 0),    V(0, 1),    1),
      (2,  V(1, 0),    V(0, -1),   -1),
      (3,  V(1, 1),    V(0, 1),    1),
      (4,  V(5, 7),    V(5, 7),    0),

      (5,  V(12, -3),  V(-5, 14),  153),
      (6,  V(phi, 1),  V(-1, phi), phi + 2),
    ]
    zero = g.Vector(0, 0)
    for i, a, b, r in cases:
      with self.subTest(i = i, a = a, b = b):
        self.assertEqual(a ^ b, r)
        self.assertEqual(b ^ a, -r)
        self.assertEqual((-a) ^ b, -r)
        self.assertEqual(a ^ (-b), -r)
        self.assertEqual((3*a) ^ b, 3*r)
        self.assertEqual(a ^ zero, 0)
        self.assertEqual(b ^ zero, 0)
        self.assertEqual(a ^ a, 0)
        self.assertEqual(b ^ b, 0)

class TestAffineTransform(TestCase):
  def test_transform_constructor_succeed(self):
    AT = g.AffineTransform
    cases = [
      ((1,2,3, 4,5,6),
          1,        2,        3,        4,        5,        6),
      ((phi,Y(1,-1),Q(1,3), 33,Q(-88,3),Y(4)),
          phi,      Y(1,-1),  Q(1,3),   33,       Q(-88,3), 4),
      ((AT(1,2,3, 4,5,6),),
          1,        2,        3,        4,        5,        6),
    ]
    for args, a, b, c, d, e, f in cases:
      with self.subTest(args = args):
        trans = g.AffineTransform(*args)
        self.assertEqual(type(trans), g.AffineTransform)
        self.assertTrue(all(
          type(x) == Y for x in [trans.a,trans.b,trans.c,trans.d,trans.e,trans.f]
        ))
        self.assertEqual(trans.a, a)
        self.assertEqual(trans.b, b)
        self.assertEqual(trans.c, c)
        self.assertEqual(trans.d, d)
        self.assertEqual(trans.e, e)
        self.assertEqual(trans.f, f)

  def test_transform_constructor_fail(self):
    AT = g.AffineTransform
    cases = [
      (0,  (1, 2, 3, 4),           TypeError),
      (1,  (1, 2, 3, 4, 5, False), TypeError),
      (2,  (15,),                  TypeError),
      (3,  (),                     TypeError),
      (4,  (AT(0,0,0,0,0,0),1),    TypeError),

      (5,  (None, 'hi there!'),    TypeError),
    ]
    for i, args, ex in cases:
      with self.subTest(i = i, args = args):
        self.assertRaises(ex, g.AffineTransform, *args)

  def test_equals(self):
    AT = g.AffineTransform
    cases = [
      (0,  AT(1,2,3, 4,5,6),           AT(1,2,3, 4,5,6),           True),
      (1,  AT(Q(1,2),0,0, 0,Q(1,2),0), AT(Q(1,2),0,0, 0,Q(1,2),0), True),
      (2,  AT(1,0,0, 0,1,0),           AT(1,0,1, 0,1,0),           False),
      (3,  AT(0,0,0, 0,0,0),           AT(1,2,3, 4,5,6),           False),
      (4,  AT(3,3,1, 3,3,2),           AT(3,3,1, 3,0,2),           False),
    ]
    for i, t1, t2, r in cases:
      with self.subTest(i = i, t1 = str(t1), t2 = str(t2)):
        self.assertEqual(t1 == t2, r)
        self.assertEqual(t2 == t1, r)
        self.assertTrue(t1 == t1)
        self.assertTrue(t2 == t2)

  def test_transform(self):
    AT, T, R, S = g.AffineTransform, g.translation, g.rotation, g.scaling
    cases = [
      (0,  AT(1,2,3, 4,5,6),    AT(3,4,8, -1,2,-12),     AT(19,26,41, 7,8,-3)),
      (1,  AT(1,0,0, 0,1,0),    AT(0,0,0, 0,0,0),        AT(0,0,0, 0,0,0)),
      (2,  T(1, 2),             T(5, 7),                 T(6, 9)),
      (3,  T(-1, 3),            S(5),                    T(-5,15)@S(5)),
      (4,  R(10),               S(-1),                   g.identity_transform),

      (5,  S(-2,2),             S(Q(-1,3),1),            S(Q(2,3),2)),
      (6,  R(5),                R(4),                    R(9)),
      (7,  T(1,1),              R(5),                    T(-1,1)@R(5)),
    ]
    for i, t1, t2, t3 in cases:
      with self.subTest(i = i, t1 = str(t1), t2 = str(t2)):
        self.assertEqual(t1.transform(t2), t3)
        self.assertEqual(t2 @ t1, t3)
        self.assertEqual(t1.transform(g.identity_transform), t1)
        self.assertEqual(t2.transform(g.identity_transform), t2)
        self.assertEqual(g.identity_transform.transform(t1), t1)
        self.assertEqual(g.identity_transform.transform(t2), t2)

  def test_negation(self):
    AT, R, S = g.AffineTransform, g.rotation, g.scaling
    cases = [
      (0,  AT(1,0,0, 0,1,0),         AT(-1,0,0, 0,-1,0)),
      (1,  AT(1,0,2, 0,1,1),         AT(-1,0,-2, 0,-1,-1)),
      (2,  AT(3,3,5, 3,7,0),         AT(-3,-3,-5, -3,-7,0)),
      (3,  R(3),                     R(13)),
      (4,  S(1,-1),                  S(-1,1)),

      (5,  S(Q(1,3)),                S(Q(-1,3))),
    ]
    for i, trans, result in cases:
      with self.subTest(i = i, trans = str(trans)):
        self.assertEqual(-trans, result)
        self.assertEqual(trans, -result)

  def test_determinant(self):
    AT, T, R, S = g.AffineTransform, g.translation, g.rotation, g.scaling
    cases = [
      (0,  AT(3,3,5, 7,-2,188),  Y(-27)),
      (1,  R(3),                 1),
      (2,  R(15),                1),
      (3,  T(2324, 500*phi),     1),
      (4,  AT(1,1,2, 0,0,234),   0),

      (5,  T(-55, 55),           1),
      (6,  S(-1),                1),
      (7,  S(-2, 3),             -6),
      (8,  S(14),                196),
    ]
    for i, trans, det in cases:
      with self.subTest(i = i, trans = str(trans)):
        self.assertEqual(trans.det(), det)
        self.assertEqual(trans.det(), det)    # sanity check for memoization
        self.assertEqual(type(trans.det()), Y)
        self.assertEqual((-trans).det(), det)

  def test_is_orientation_preserving(self):
    AT, T, R, S = g.AffineTransform, g.translation, g.rotation, g.scaling
    cases = [
      (0,  AT(3,0,23, 0,2,-1000),    True),
      (1,  R(14),                    True),
      (2,  T(23523, Y(0,-2334)),     True),
      (3,  g.identity_transform,     True),
      (4,  S(100),                   True),

      (5,  S(-100),                  True),
      (6,  S(-1, 1),                 False),
      (7,  S(-5, -7),                True),
      (8,  R(2) @ S(5),              True),
    ]
    for i, trans, result in cases:
      with self.subTest(i = i, trans = str(trans)):
        self.assertEqual(trans.is_orientation_preserving(), result)
        self.assertEqual(trans.is_orientation_preserving(), result)

  def test_is_conformal(self):
    AT, T, R, S = g.AffineTransform, g.translation, g.rotation, g.scaling
    cases = [
      (0,  g.identity_transform,      True),
      (1,  S(-5),                     True),
      (2,  S(15),                     True),
      (3,  S(-5, 5),                  True),
      (4,  S(0),                      True),
      (5,  AT(3,3,2, 3,3,18),         False),
      (6,  T(5, phi*3),               True),
      (7,  R(1),                      True),
      (8,  AT(0,0,8, 0,1,9),          False),
    ]
    for i, trans, result in cases:
      with self.subTest(i = i, trans = str(trans)):
        self.assertEqual(trans.is_conformal(), result)
        self.assertEqual(trans.is_conformal(), result)

class TestTransformFunctions(TestCase):
  def test_identity_transform(self):
    cases = [
      g.Point(25, Q(-5,6)),
      g.Vector(4, 6),
      g.AffineTransform(1,2,3, 4,5,6),

      g.Point(0, 0),
      g.Point(1, 0),
      g.Point(0, 1),

      g.Vector(0, 0),
      g.Vector(1, 0),
      g.Vector(0, 1),
    ]
    identity = g.identity_transform
    for c in cases:
      with self.subTest(case = str(c)):
        self.assertEqual(c.transform(identity), c)
        self.assertEqual(identity @ c, c)

  def test_rotation(self):
    P, V, AT = g.Point, g.Vector, g.AffineTransform
    cases = [
      (0,  0,   P(1, 0),          P(1, 0)),
      (1,  5,   P(1, 0),          P(0, 1)),
      (2,  -15, P(0, 1),          P(-1, 0)),
      (3,  0,   V(0, 2),          V(0, 2)),
      (4,  1,   V(0, 3),          V(Y(Q(9,2),0,Q(-3,8),0), Y(0,Q(3,4)))),

      (5,  10,  V(3, 55),         V(-3, -55)),
      (6,  5,   AT(3,0,2, 0,3,8), AT(0,-3,-8, 3,0,2)),
    ]
    for i, theta, x, r in cases:
      with self.subTest(i = i, x = str(x), theta = theta):
        self.assertEqual(x.transform(g.rotation(theta)), r)
        self.assertEqual(x, r.transform(g.rotation(-theta)))

  def test_scaling(self):
    V, P, S = g.Vector, g.Point, g.scaling
    cases = [
      (0,  (1,),      V(1, 0),      V(1, 0)),
      (1,  (1,),      V(0, 1),      V(0, 1)),
      (2,  (2, 3),    V(4, 5),      V(8, 15)),
      (3,  (-2,),     P(1, 2),      P(-2, -4)),
      (4,  (1, 4),    S(Q(1,2)),    S(Q(1,2),2)),

      (5,  (-2,),     P(1, 17),     P(-2, -34)),
    ]
    for i, args, x, r in cases:
      with self.subTest(i = i, x = str(x), args = args):
        trans = g.scaling(*args)
        self.assertEqual(x.transform(trans), r)

  def test_translation(self):
    P, V, AT = g.Point, g.Vector, g.AffineTransform
    cases = [
      (0,  (3,5),      P(1, 2),          P(4, 7)),
      (1,  (3,5),      V(1, 2),          V(1, 2)),
      (2,  (V(3,5),),  P(1, 2),          P(4, 7)),
      (3,  (-8,2),     AT(1,2,3, 4,5,6), AT(1,2,-5, 4,5,8)),
      (4,  (V(-8,2),), AT(1,2,3, 4,5,6), AT(1,2,-5, 4,5,8)),

      (5,  (4,-10),    P(5, -7),         P(9, -17)),
      (6,  (4,-10),    V(5, -7),         V(5, -7)),
    ]
    for i, args, x, r in cases:
      with self.subTest(i = i, x = str(x), args = args):
        trans = g.translation(*args)
        self.assertEqual(x.transform(trans), r)

class TestLineSegment(TestCase):
  def test_constructor_succeed(self):
    P, V = g.Point, g.Vector
    cases = [
      (0,  (P(0,0),  P(1,0)),             P(0,0),       P(1,0),        V(1,0)),
      (1,  (P(1,0),  P(0,0)),             P(1,0),       P(0,0),        V(-1,0)),
      (2,  (P(-3,5), V(3,Q(2,3))),        P(-3,5),      P(0,Q(17,3)),  V(3,Q(2,3))),
      (3,  (P(inv_phi,2), P(phi,-sqrt5)), P(inv_phi,2), P(phi,-sqrt5), V(1,-(2+sqrt5))),
      (4,  (P(14,2), V(-14,-2)),          P(14,2),      P(0,0),        V(-14,-2)),
    ]
    for i, args, begin, end, d in cases:
      with self.subTest(i = i, args = args):
        seg = g.LineSegment(*args)
        self.assertEqual(type(seg), g.LineSegment)
        self.assertEqual(seg.begin, begin)
        self.assertEqual(seg.end, end)
        self.assertEqual(seg.direction, d)

  def test_constructor_fail(self):
    P, V = g.Point, g.Vector
    cases = [
      (0,  (P(1,2),),        TypeError),
      (1,  (V(3,2), P(0,1)), TypeError),
      (2,  (P(3,3), P(3,3)), ValueError),
      (3,  (V(5,phi),),      TypeError),
      (4,  (),               TypeError),

      (5,  (P(14,6),V(0,0)), ValueError),
      (6,  (P(0,0),),        TypeError),
    ]
    for i, args, ex in cases:
      with self.subTest(i = i, args = args):
        self.assertRaises(ex, g.LineSegment, *args)

  def test_equality(self):
    LS = lambda d, e: g.LineSegment(g.Point(*d), g.Point(*e))
    cases = [
      (0,  LS((0,0), (1,0)),       LS((0,0), (1,0)),    True),
      (1,  LS((0,0), (1,0)),       LS((1,0), (0,0)),    False), # order matters!
      (2,  LS((3,sqrt5), (5,2)),   LS((-3,-sqrt5), (-5,-2)), False),
      (3,  LS((5,3), (2,1)),       g.LineSegment(g.Point(5,3), g.Vector(-3,-2)), True),
      (4,  LS((3,inv_phi), (1,1)), LS((3,phi-1), (1,1)), True),

      (5,  LS((1,2), (3,4)),       LS((1,2), (3,4)),    True),
      (6,  LS((1,2), (3,4)),       LS((1,2), (3,5)),    False),
      (7,  LS((1,2), (3,4)),       LS((1,2), (4,4)),    False),
      (8,  LS((1,2), (3,4)),       LS((1,3), (3,4)),    False),
      (9,  LS((1,2), (3,4)),       LS((0,2), (3,4)),    False),

      (10, LS((1,2), (88,4)),      LS((2,3), (89,5)),   False), # same direction, but still different
    ]
    for i, a, b, result in cases:
      with self.subTest(i = i, a = str(a), b = str(b)):
        self.assertEqual(a == b, result)
        self.assertEqual(b == a, result)
        self.assertEqual(a != b, not result)
        self.assertEqual(b != a, not result)

  def test_addition(self):
    LS = lambda d, e: g.LineSegment(g.Point(*d), g.Point(*e))
    V = g.Vector
    cases = [
      (0,  LS((5,7), (3,2)),      V(0,0),      LS((5,7), (3,2))),
      (1,  LS((5,7), (3,2)),      V(-5,-7),    LS((0,0), (-2,-5))),
      (2,  LS((-phi,0),(0,phi)),  V(phi, phi), LS((0,phi), (phi,2*phi))),
      (3,  LS((0,0), (1,0)),      V(0,-1),     LS((0,-1), (1,-1))),
    ]
    for i, seg, v, r in cases:
      with self.subTest(i = i, seg = str(seg), v = str(v)):
        self.assertEqual(seg + v, r)
        self.assertEqual(v + seg, r)

  def test_transform_succeed(self):
    LS = lambda d, e: g.LineSegment(g.Point(*d), g.Point(*e))
    AT, I, T, R, S = g.AffineTransform, g.identity_transform, g.translation, g.rotation, g.scaling
    cases = [
      (0,  LS((0,0), (1,0)),        I,          LS((0,0), (1,0))),
      (1,  LS((3,5), (18,-7)),      I,          LS((3,5), (18,-7))),
      (2,  LS((2,3), (4,5)),        R(5),       LS((-3,2), (-5,4))),
      (3,  LS((phi,0), (phi,-phi)), S(inv_phi), LS((1,0), (1,-1))),
    ]
    for i, seg, trans, r in cases:
      with self.subTest(i = i, seg = str(seg), trans = str(trans)):
        self.assertEqual(seg.transform(trans), r)
        self.assertEqual(trans @ seg, r)

  def test_transform_fail(self):
    LS = lambda d, e: g.LineSegment(g.Point(*d), g.Point(*e))
    AT, S = g.AffineTransform, g.scaling
    cases = [
      (0,  LS((15,8), (-20,7)),   S(0),    ValueError),
      (1,  LS((15,8), (-20,8)),   S(0,1),  ValueError),
      (2,  LS((15,8), (15,7)),    S(-1,0), ValueError),
      (3,  LS((12,8), (1,19)),    AT(1,1,4, -1,-1,7),  ValueError),
    ]
    for i, seg, trans, ex in cases:
      with self.subTest(i = i, seg = str(seg), trans = str(trans)):
        self.assertRaises(ex, lambda s, t: s.transform(t), seg, trans)
        self.assertRaises(ex, lambda s, t: t @ s, seg, trans)

  def test_bbox(self):
    LS = lambda d, e: g.LineSegment(g.Point(*d), g.Point(*e))
    R = g.Rectangle
    cases = [
      (0,  LS((0,0), (1,0)),      R(0,0,1,0)),
      (1,  LS((3,5), (2,17)),     R(2,5,3,17)),
      (2,  LS((-2,-phi), (-2,1)), R(-2,-phi,-2,1)),
      (3,  LS((15,9), (3,2)),     R(3,2,15,9)),
    ]
    for i, seg, bbox in cases:
      with self.subTest(i = i, seg = str(seg)):
        self.assertEqual(seg.bbox(), bbox)

class TestRectangle(TestCase):
  def test_constructor_succeed(self):
    P, V = g.Point, g.Vector
    cases = [
      (0,  (P(1,2), P(3,5)),     Y(1),   Y(2),   Y(3),   Y(5)),
      (1,  (14, 2, -6, 8),       Y(-6),  Y(2),   Y(14),  Y(8)),
      (2,  (P(13,8), V(-4,-5)),  9,      3,      13,     8),
      (3,  (V(0,0), P(5,2)),     5,      2,      5,      2),
      (4,  (4, 5, -6, -7),       -6,     -7,     4,      5),

      (5,  (P(Q(1,2), Q(3,2)), V(1,1)),
                                 Q(1,2), Q(3,2), Q(3,2), Q(5,2)),
    ]
    for i, args, minx, miny, maxx, maxy in cases:
      with self.subTest(i = i, args = args):
        r = g.Rectangle(*args)
        self.assertEqual(type(r), g.Rectangle)
        self.assertTrue(type(x) == Y for x in [r.min_x,r.min_y,r.max_x,r.max_y])
        self.assertEqual(r.min_x, minx)
        self.assertEqual(r.min_y, miny)
        self.assertEqual(r.max_x, maxx)
        self.assertEqual(r.max_y, maxy)

  def test_constructor_fail(self):
    P, V, LS = g.Point, g.Vector, g.LineSegment
    cases = [
      (0,  (),                    TypeError),
      (1,  (P(3,5),),             TypeError),
      (2,  (V(1,7),),             TypeError),
      (3,  (V(5,5), V(1,2)),      TypeError),
      (4,  (LS(P(0,0), P(1,2)),), TypeError),

      (5,  (P(3,4), 45, 2),       TypeError),
      (6,  (3, 4, P(45, 2)),      TypeError),
      (7,  (1, 2, 3, 'hi!'),      TypeError),
    ]
    for i, args, ex in cases:
      with self.subTest(i = i, args = args):
        self.assertRaises(ex, g.Rectangle, ex)

  def test_equality(self):
    R = g.Rectangle
    cases = [
      (0,  R(0,0,0,0),    R(0,0,0,0),      True),
      (1,  R(0,0,0,0),    R(0,0,0,1),      False),
      (2,  R(-1,0,0,0),   R(0,0,0,0),      False),
      (3,  R(5,phi,8,2),  R(8,phi,5,2),    True),
      (4,  R(35,8,90,8),  R(90,8,35,8),    True),

      (5,  R(Q(1,1000),2,-5,3),
                          R(-5,2,0,3),     False),
      (6,  R(1,2,3,4),    g.LineSegment(g.Point(1,2), g.Point(3,4)),
                                           False),
      (7,  R(1,2,1,2),    g.Point(1,2),    False),
    ]
    for i, a, b, r in cases:
      with self.subTest(i = i, a = str(a), b = str(b)):
        self.assertEqual(a == b, r)
        self.assertEqual(b == a, r)
        self.assertEqual(a != b, not r)
        self.assertEqual(b != a, not r)

  def test_bbox(self):
    R = g.Rectangle
    cases = [
      (0,  R(1,2,4,3)),
      (1,  R(8,2,1,1)),
      (2,  R(0,0,0,0)),
      (3,  R(0,0,1,0)),
      (4,  R(0,0,0,1)),

      (5,  R(-213,239,Q(2382839,4),-sqrt5)),
    ]
    for i, rect in cases:
      with self.subTest(i = i, rect = str(rect)):
        self.assertEqual(rect.bbox(), rect)

class TestDoBboxesOverlap(TestCase):
  def test_do_bboxes_overlap(self):
    R = g.Rectangle
    cases = [
      (0,  R(1,2,3,4),     R(-1,-2,-3,-4),      False),
      (1,  R(1,2,3,4),     R(1,2,3,4),          True),
      (2,  R(1,2,3,4),     R(3,4,5,6),          True), # event single-point overlap counts
      (3,  R(13,4,13,8),   R(13,8,13,10),       True),
      (4,  R(13,4,13,8),   R(13,21,13,99),      False),

      (5,  R(-13,4,-13,8), R(-13,5,-13,7),      True),
      (6,  R(-13,4,-13,8), R(-13,6,-13,10),     True),
      (7,  R(1,2,3,4),     R(3,3,8,5),          True),
      (8,  R(1,2,1,2),     R(1,2,1,2),          True),
      (9,  R(1,2,1,2),     R(0,0,4,4),          True),

      (10, R(1,2,1,2),     R(-2,-2,-4,-4),      False),
    ]
    for i, a, b, r in cases:
      with self.subTest(i = i, a = str(a), b = str(b)):
        self.assertEqual(g.do_bboxes_overlap(a, b), r)
        self.assertEqual(g.do_bboxes_overlap(b, a), r)

class TestPolygon(TestCase):
  def test_constructor_succeed(self):
    P = g.Point
    a2 = ((1,5), (2,6), (-1,7))
    cases = [
      (0,  (P(0,0), P(1,0), P(0,1)),            3),
      (1,  (P(0,0), P(1,0), P(1,1), P(0,1)),    4),
      (2,  ([P(0,0), P(2,0), P(2,2)],),         3), # list
      (3,  ((P(2,0), P(2,2), P(0,0)),),         3), # tuple
      (4,  ((g.Point(*coords) for coords in a2),), 3), # generator

      (5,  (P(3,0), P(1,1), P(0,3), P(-1,1), P(-3,0), P(-1,-1), P(0,-3), P(1,-1)), 8),
    ]
    for i, args, n in cases:
      with self.subTest(i = i, args = args):
        poly = g.Polygon(*args)
        self.assertEqual(type(poly), g.Polygon)
        self.assertEqual(len(poly._v), n)
        e = poly.edges()
        self.assertEqual(len(poly._e), n)

  def test_constructor_fail(self):
    P = g.Point
    cases = [
      (0,  (),                                  ValueError),
      (1,  ([P(0,0), P(1,0), P(1,1)], P(0,1)),  TypeError),
      (2,  ([P(0,0), P(1,0), P(1,1)], [P(-3,2), P(-4,2), P(-4,1)]), TypeError),
      (3,  (P(3,2), P(4,1)),                    ValueError),
      (4,  (P(4,4),),                           ValueError),

      (5,  (P(3,2), P(4,4), P(5,2), 'hi!'),     TypeError),
      (6,  ('hi!'),                             TypeError),
    ]
    for i, args, ex in cases:
      with self.subTest(i = i, args = args):
        self.assertRaises(ex, g.Polygon, *args)

  _test_polygons = {
  }

  _test_polygon_data = {
    'simple-triangle': ((0,0), (1,0), (0,1)),
    'non-convex-quad': ((0,0), (3,0), (1,1), (0,3)),
    'unit-pentagon':   ((p.x, p.y) for p in (g.Point(1,0).rotate(4*n) for n in range(5))),
    'zig-zag':         ((0,0), (2,0), (2,2), (4,2), (4,4),
                        (4,5), (3,5), (3,3), (1,3), (1,1)),
  }

  _up_pt1 = g.Point(1,0).rotate(4)
  _up_pt2 = _up_pt1.rotate(4)
  _up_pt3 = _up_pt2.rotate(4)
  _up_pt4 = _up_pt3.rotate(4)

  @classmethod
  def setUpClass(cls):
    for k, v in cls._test_polygon_data.items():
      cls._test_polygons[k] = g.Polygon(g.Point(*coord) for coord in v)

  def test_vertices(self):
    cases = [
      ('simple-triangle',  [(0,0), (1,0), (0,1)]),
      ('non-convex-quad',  [(0,0), (3,0), (1,1), (0,3)]),
      ('unit-pentagon',    [(1,0), (self._up_pt1.x,self._up_pt1.y),
                                   (self._up_pt2.x,self._up_pt2.y),
                                   (self._up_pt3.x,self._up_pt3.y),
                                   (self._up_pt4.x,self._up_pt4.y)]),
      ('zig-zag', [(0,0), (2,0), (2,2), (4,2), (4,4), (4,5), (3,5), (3,3), (1,3), (1,1)]),
    ]
    for i, r in cases:
      with self.subTest(polyName = i):
        poly = self._test_polygons[i]
        self.assertEqual(len(poly.vertices()), len(r))
        self.assertTrue(all(
          (type(v_poly) == g.Point and v_poly == v_r)
          for v_poly, v_r
          in zip_longest(poly.vertices(), (g.Point(*c) for c in r))
        ))

  def test_edges(self):
    LS = lambda d, e: g.LineSegment(g.Point(*d), g.Point(*e))
    LS2 = g.LineSegment
    cases = [
      ('simple-triangle', [LS((0,0), (1,0)), LS((1,0), (0,1)), LS((0,1), (0,0))]),
      ('non-convex-quad', [LS((0,0), (3,0)), LS((3,0), (1,1)),
                           LS((1,1), (0,3)), LS((0,3), (0,0))]),
      ('unit-pentagon',   [LS2(g.Point(1,0), self._up_pt1),
                           LS2(self._up_pt1, self._up_pt2),
                           LS2(self._up_pt2, self._up_pt3),
                           LS2(self._up_pt3, self._up_pt4),
                           LS2(self._up_pt4, g.Point(1,0))]),
      ('zig-zag',         [LS((0,0), (2,0)), LS((2,0), (2,2)),
                           LS((2,2), (4,2)), LS((4,2), (4,4)),
                           LS((4,4), (4,5)), LS((4,5), (3,5)),
                           LS((3,5), (3,3)), LS((3,3), (1,3)),
                           LS((1,3), (1,1)), LS((1,1), (0,0))]),
    ]
    for i, r in cases:
      with self.subTest(polyName = i):
        poly = self._test_polygons[i]
        self.assertEqual(len(poly.edges()), len(r))
        self.assertTrue(all(
          (type(e_poly) == g.LineSegment and e_poly == e_r)
          for e_poly, e_r
          in zip_longest(poly.edges(), r)
        ))

  def test_is_convex(self):
    cases = [
      ('simple-triangle', True),
      ('non-convex-quad', False),
      ('unit-pentagon',   True),
      ('zig-zag',         False),
    ]
    for i, r in cases:
      with self.subTest(polyName = i):
        poly = self._test_polygons[i]
        self.assertEqual(poly.is_convex(), r)
        self.assertEqual(poly.is_convex(), r)

  def test_bbox(self):
    R = g.Rectangle
    cases = [
      ('simple-triangle', R(0, 0, 1, 1)),
      ('non-convex-quad', R(0, 0, 3, 3)),
      ('unit-pentagon',   R(self._up_pt2.x, self._up_pt4.y, 1, self._up_pt1.y)),
      ('zig-zag',         R(0, 0, 4, 5)),
    ]
    for i, bbox in cases:
      with self.subTest(polyName = i, pb = str(self._test_polygons[i].bbox())):
        poly = self._test_polygons[i]
        self.assertEqual(poly.bbox(), bbox)
        self.assertEqual(poly.bbox(), bbox)

class TestPolygonAlgorithms(TestCase):
  _test_polygons = {
    'unit-pentagon': g.Polygon(g.rotation(4*n) @ g.Point(1, 0) for n in range(5)),
  }

  _test_polygon_data = {
    'simple-triangle': [(0,0), (1,0), (0,1)],
    'diamond':         [(1,0), (0,1), (-1,0), (0,-1)],
    'tri2':            [(0,0), (1,0), (1,1)],
    'tri3':            [(1,0), (1,1), (0,1)],
    'tri4':            [(1,1), (0,1), (0,0)],
    'non-convex-quad': [(0,0), (3,0), (1,1), (0,3)],
    'zig-zag':         [(0,0), (2,0), (2,2), (4,2), (4,4),
                        (4,5), (3,5), (3,3), (1,3), (1,1)],

    'intersect1':      [(1,Q(1,3)), (0,1), (-1,Q(1,3))],
    'intersect2':      [(0,0), (1,Q(2,3)), (-1,Q(2,3))],
    'i2-other-way':    [(-1,Q(2,3)), (1,Q(2,3)), (0,0)],

    'vintersect1':     [(0,0), (Q(2,3),-1), (Q(2,3),1)],
    'vintersect2':     [(Q(1,3),-1), (1,0), (Q(1,3),1)],
    'vi2-other-way':   [(Q(1,3),1), (1,0), (Q(1,3),-1)],

    'close-noint1':    [(0,0), (Q(5,6),0), (0,Q(5,6))],
    'close-noint2':    [(1,Q(1,6)), (1,1), (Q(1,6),1)],

    # the next three are polygons with vertex-to-vertex or vertex-to-edge
    # intersections with unit-pentagon
    'pt-inter-pent1':  [(2,-1), (1,0), (2,1)],
    'pt-inter-pent2':  [(1,-1), (2,0), (1,1)],
    'pt-inter-pent3':  [(Y(1,0,Q(-1,8)),0), (-1,-1), (-1,1)],

    'edge_int1':       [(0,0), (2,0), (0,1)],
    'edge_int2':       [(2,1), (0,1), (2,0)],
    'edge_int2-other': [(2,0), (0,1), (2,1)],
    'edge_int1-rot1':  [(2,0), (0,1), (0,0)],
    'edge_int1-rot2':  [(0,1), (0,0), (2,0)],

    'h_edge_int1':     [(1,Q(1,3)), (0,1), (-1,Q(1,3))],
    'h_edge_int2':     [(1,Q(1,3)), (-1,Q(1,3)), (0,-1)],

    'v_edge_int1':     [(1,-1), (0,0), (1,1)],
    'v_edge_int2':     [(1,1), (1,-1), (2,0)],

    'intersect-pent4': [(0,0), (57,56), (56,57)],
    'intersect-pent5': [(Q(1,2),0), (0,Q(1,2)), (Q(-1,2),0), (0,Q(-1,2))],
  }

  @classmethod
  def setUpClass(cls):
    for k, v in cls._test_polygon_data.items():
      cls._test_polygons[k] = g.Polygon(g.Point(*coord) for coord in v)
    pent = cls._test_polygons['unit-pentagon']
    pent2 = (g.translation(2 * pent.vertices()[2].x, 0) @ g.rotation(10)) @ pent
    v1 = pent.vertices()[1]
    pent3 = (g.translation(v1.x, v1.y) @ g.rotation(10) @ g.translation(-1,0)) @ pent
    cls._test_polygons['up-2'] = pent2
    cls._test_polygons['up-3'] = pent3

  def test_point_in_polygon(self):
    cases = [
      ('simple-triangle', (0, 0),              0),
      ('simple-triangle', (inv_phi,1-inv_phi), 0),
      ('simple-triangle', (Q(3,4), Q(1,2)),   -1),
      ('simple-triangle', (Q(1,2), Q(3,4)),   -1),
      ('simple-triangle', (Q(3,4), Q(1,4)),    0),
      ('simple-triangle', (Q(1,4), Q(1,4)),   +1),

      ('diamond',         (Q(1,4), Q(3,4)),    0),
      ('diamond',         (3, 5),             -1),

      ('diamond',         (0, 8),             -1),
      ('diamond',         (8, 0),             -1),
      ('diamond',         (0, -8),            -1),
      ('diamond',         (-8, 0),            -1),

      ('diamond',         (0, 1),              0),
      ('diamond',         (1, 0),              0),
      ('diamond',         (0, -1),             0),
      ('diamond',         (-1, 0),             0),

      ('diamond',         (Q(1,8), 0),        +1),
      ('diamond',         (0, Q(1,8)),        +1),
      ('diamond',         (Q(-1,8), 0),       +1),
      ('diamond',         (0, Q(-1,8)),       +1),

      ('diamond',         (0, 0),             +1),
    ]
    for i, coords, r in cases:
      with self.subTest(polyName = i, x = coords[0], y = coords[1]):
        poly = self._test_polygons[i]
        pt = g.Point(*coords)
        self.assertEqual(g.point_in_polygon(pt, poly), r)

  def test_point_in_polygon_pictorial(self):
    P = lambda x: g.Polygon(g.Point(*coord) for coord in x)
    sgn_str = lambda x: '-' if x < 0 else ('+' if x > 0 else '0')

    numbers = (-inv_phi, Q(-1,2), inv_phi-1, Q(-1,4), 0, Q(1,4), 1-inv_phi, Q(1,2), inv_phi, Q(3,4), 1, Q(5,4), phi)
    numbers = [Y(x) for x in numbers]
    numbers_rev = numbers.copy()
    numbers_rev.reverse()

    pics = {
      'simple-triangle': ('-------------',
                          '-------------',
                          '----0--------',
                          '----00-------',
                          '----0+0------',
                          '----0++0-----',
                          '----0+++0----',
                          '----0++++0---',
                          '----0000000--',
                          '-------------',
                          '-------------',
                          '-------------',
                          '-------------'),
      'diamond':         ('-------------',
                          '-------------',
                          '----0--------',
                          '---0+0-------',
                          '--0+++0------',
                          '-0+++++0-----',
                          '0+++++++0----',
                          '+++++++++0---',
                          '++++++++++0--',
                          '+++++++++0---',
                          '0+++++++0----',
                          '-0+++++0-----',
                          '--0+++0------'),
      'tri2':            ('-------------',
                          '-------------',
                          '----------0--',
                          '---------00--',
                          '--------0+0--',
                          '-------0++0--',
                          '------0+++0--',
                          '-----0++++0--',
                          '----0000000--',
                          '-------------',
                          '-------------',
                          '-------------',
                          '-------------'),
      'tri3':            ('-------------',
                          '-------------',
                          '----0000000--',
                          '-----0++++0--',
                          '------0+++0--',
                          '-------0++0--',
                          '--------0+0--',
                          '---------00--',
                          '----------0--',
                          '-------------',
                          '-------------',
                          '-------------',
                          '-------------'),
      'tri4':            ('-------------',
                          '-------------',
                          '----0000000--',
                          '----0++++0---',
                          '----0+++0----',
                          '----0++0-----',
                          '----0+0------',
                          '----00-------',
                          '----0--------',
                          '-------------',
                          '-------------',
                          '-------------',
                          '-------------'),
      'non-convex-quad': ('----0++++----',
                          '----0+++++---',
                          '----0+++++0--',
                          '----0+++++++-',
                          '----0++++++++',
                          '----0++++++++',
                          '----0++++++++',
                          '----0++++++++',
                          '----000000000',
                          '-------------',
                          '-------------',
                          '-------------',
                          '-------------'),
    }
    for i in pics:
      with self.subTest(polyName = i):
        poly = self._test_polygons[i]
        pic_actual = []
        for y in numbers_rev:
          s = ''.join(sgn_str(g.point_in_polygon(g.Point(x, y), poly)) for x in numbers)
          pic_actual.append(s)
        pic_actual = tuple(pic_actual)
        pic_expected = pics[i]
        self.assertTrue(pic_actual == pic_expected,
          msg = '\nexpected:\n{ex}\n\nactual:\n{ac}\n'.format(
            ex = '\n'.join(pic_expected),
            ac = '\n'.join(pic_actual)
          )
        )

  def test_do_convex_polygons_intersect(self):
    cases = [
      ('intersect1',     'intersect2',      (True,  True,  None)),
      ('intersect1',     'i2-other-way',    (True,  True,  None)),
      ('intersect1',     'intersect1',      (True,  True,  None)),
      ('intersect2',     'i2-other-way',    (True,  True,  None)),

      ('close-noint1',   'close-noint2',    (False, False, None)),

      ('unit-pentagon',  'pt-inter-pent1',  (True,  False, None)),
      ('unit-pentagon',  'pt-inter-pent2',  (True,  False, None)),
      ('unit-pentagon',  'pt-inter-pent3',  (True,  False, None)),

      ('edge_int1',      'edge_int2',       (True,  False, (1, 1))),
      ('edge_int1',      'edge_int2-other', (True,  False, (1, 0))),
      ('edge_int1-rot1', 'edge_int2',       (True,  False, (0, 1))),
      ('edge_int1-rot2', 'edge_int2',       (True,  False, (2, 1))),
      ('edge_int1-rot2', 'edge_int2-other', (True,  False, (2, 0))),

      ('h_edge_int1',    'h_edge_int2',     (True,  False, (2, 0))),
      ('v_edge_int1',    'v_edge_int2',     (True,  False, (2, 0))),

      ('unit-pentagon',  'intersect-pent4', (True,  True,  None)),
      ('unit-pentagon',  'intersect-pent5', (True,  True,  None)),
    ]

    flip3 = lambda t: t if (t[2] is None) else (t[0], t[1], (t[2][1], t[2][0]))

    for i1, i2, r in cases:
      with self.subTest(polyName1 = i1, polyName2 = i2):
        poly1 = self._test_polygons[i1]
        poly2 = self._test_polygons[i2]
        self.assertEqual(g.do_convex_polygons_intersect(poly1, poly2), r)
        self.assertEqual(g.do_convex_polygons_intersect(poly2, poly1), flip3(r))

  def test_do_convex_polygons_intersect_exceptions(self):
    cases = [
      ('unit-pentagon', 'non-convex-quad', ValueError),
    ]
    for i1, i2, ex in cases:
      with self.subTest(polyName1 = i1, polyName2 = i2):
        poly1 = self._test_polygons[i1]
        poly2 = self._test_polygons[i2]
        self.assertRaises(ex, g.do_convex_polygons_intersect, poly1, poly2)
