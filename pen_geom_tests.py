from unittest import TestCase, skip
import pen_geom as g
from fractions import Fraction as Q
from pen_num import Number as Y, phi, inv_phi, sqrt5, alpha

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

  @skip('not fully implemented yet')
  def test_translation(self):
    cases = [
    ]
    for args, x, r in cases:
      with self.subTest(x = x, args = args):
        trans = g.translation(*args)
        self.assertEqual(x.transform(trans), r)

class TestLineSegment(TestCase):
  @skip('not fully implemented yet')
  def test_constructor_succeed(self):
    cases = [
    ]
    for args, begin, end, d in cases:
      with self.subTest(args = args):
        seg = g.LineSegment(*args)
        self.assertEqual(type(seg), g.LineSegment)
        self.assertEqual(seg.begin, begin)
        self.assertEqual(seg.end, end)
        self.assertEqual(seg.direction, d)

  @skip('not fully implemented yet')
  def test_constructor_fail(self):
    cases = [
    ]
    for args, ex in cases:
      with self.subTest(args = args):
        self.assertRaises(ex, g.LineSegment, *args)

  @skip('not fully implemented yet')
  def test_equality(self):
    cases = [
    ]
    for a, b, result in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a == b, result)
        self.assertEqual(b == a, result)
        self.assertEqual(a != b, not result)
        self.assertEqual(b != a, not result)

  @skip('not fully implemented yet')
  def test_addition(self):
    cases = [
    ]
    for seg, v, r in cases:
      with self.subTest(seg = seg, v = v):
        self.assertEqual(seg + v, r)
        self.assertEqual(v + seg, r)

  @skip('not fully implemented yet')
  def test_transform(self):
    cases = [
    ]
    for seg, trans, r in cases:
      with self.subTest(seg = seg, trans = trans):
        self.assertEqual(seg.transform(trans), r)
        self.assertEqual(trans @ seg, r)

  @skip('not fully implemented yet')
  def test_bbox(self):
    cases = [
    ]
    for seg, bbox in cases:
      with self.subTest(seg = seg):
        self.assertEqual(seg.bbox(), bbox)

class TestRectangle(TestCase):
  @skip('not fully implemented yet')
  def test_constructor_succeed(self):
    cases = [
    ]
    for args, minx, miny, maxx, maxy in cases:
      with self.subTest(args = args):
        r = g.Rectangle(*args)
        self.assertEqual(type(r), g.Rectangle)
        self.assertEqual(r.min_x, minx)
        self.assertEqual(r.min_y, miny)
        self.assertEqual(r.max_x, maxx)
        self.assertEqual(r.max_y, maxy)

  @skip('not fully implemented yet')
  def test_constructor_fail(self):
    cases = [
    ]
    for args, ex in cases:
      with self.subTests(args = args):
        self.assertRaises(ex, g.Rectangle, ex)

  @skip('not fully implemented yet')
  def test_equality(self):
    cases = [
    ]
    for a, b, r in cases:
      with self.subTests(a = a, b = b):
        self.assertEqual(a == b, r)
        self.assertEqual(b == a, r)
        self.assertEqual(a != b, not r)
        self.assertEqual(b != a, not r)

  @skip('not fully implemented yet')
  def test_bbox(self):
    cases = [
    ]
    for rect, bbox in cases:
      with self.subTests(rect = rect):
        self.assertEqual(rect.bbox(), rect)

class TestDoBboxesOverlap(TestCase):
  @skip('not fully implemented yet')
  def test_do_bboxes_overlap(self):
    cases = [
    ]
    for a, b, r in cases:
      with self.subTests(a = a, b = b):
        self.assertEqual(do_bboxes_overlap(a, b), r)
        self.assertEqual(do_bboxes_overlap(b, a), r)

class TestPolygon(TestCase):
  _test_polygons = {
  }

  @skip('not fully implemented yet')
  def test_constructor_succeed(self):
    cases = [
    ]
    for args, n in cases:
      with self.subTests(args = args):
        poly = g.Polygon(*args)
        self.assertEqual(type(poly), g.Polygon)
        self.assertEqual(len(poly._v), n)
        self.assertEqual(len(poly._e), n)

  @skip('not fully implemented yet')
  def test_constructor_fail(self):
    cases = [
    ]
    for args, ex in cases:
      with self.subTests(args = args):
        self.assertRaises(ex, g.Polygon, *args)

  @skip('not fully implemented yet')
  def test_vertices(self):
    cases = [
    ]
    for args, r in cases:
      with self.subTest(args = args):
        poly = g.Polygon(*args)
        self.assertEqual(len(poly.vertices()), len(r))
        self.assertTrue(all(v_poly == v_r for v_poly, v_r in zip(poly.vertices(), r)))

  @skip('not fully implemented yet')
  def test_edges(self):
    cases = [
    ]
    for args, r in cases:
      with self.subTest(args = args):
        poly = g.Polygon(*args)
        self.assertEqual(len(poly.edges()), len(r))
        self.assertTrue(all(e_poly == e_r for e_poly, e_r in zip(poly.edges(), r)))

  @skip('not fully implemented yet')
  def test_is_convex(self):
    cases = [
    ]
    for i, r in cases:
      with self.subTest(polyName = i):
        poly = self._test_polygons[i]
        self.assertEqual(poly.is_convex(), r)
        self.assertEqual(poly.is_convex(), r)

  @skip('not fully implemented yet')
  def test_bbox(self):
    cases = [
    ]
    for i, bbox in cases:
      with self.subTest(polyName = i):
        poly = self._test_polygons[i]
        self.assertEqual(poly.bbox(), bbox)
        self.assertEqual(poly.bbox(), bbox)

class TestPolygonAlgorithms(TestCase):
  _test_polygons = {
    'unit-pentagon': g.Polygon(g.rotation(4*n) @ g.Point(1, 0) for n in range(5)),
  }

  @skip('not fully implemented yet')
  def test_point_in_polygon(self):
    cases = [
    ]
    for i, coords, r in cases:
      with self.subTest(polyName = i, x = coords[0], y = coords[1]):
        poly = self._test_polygons[i]
        pt = g.Point(*coords)
        self.assertEqual(g.point_in_polygon(pt, poly), r)

  @skip('not fully implemented yet')
  def test_do_convex_polygons_intersect(self):
    cases = [
    ]
    for i1, i2, r in cases:
      with self.subTest(polyName1 = i1, polyName2 = i2):
        poly1 = self._test_polygons[i1]
        poly2 = self._test_polygons[i2]
        self.assertEqual(g.do_convex_polygons_intersect(poly1, poly2), r)
        self.assertEqual(g.do_convex_polygons_intersect(poly2, poly1), r)

  @skip('not fully implemented yet')
  def test_do_convex_polygons_intersect_exceptions(self):
    cases = [
    ]
    for i1, i2, ex in cases:
      with self.subTest(polyName1 = i1, polyName2 = i2):
        poly1 = self._test_polygons[i1]
        poly2 = self._test_polygons[i2]
        self.assertRaises(ex, g.do_convex_polygons_intersect, poly1, poly2)
