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
      (P(-5, phi),    V(-5, phi))
    ]
    for pt, vec in cases:
      with self.subTest(pt = pt):
        self.assertEqual(pt.as_offset_vector(), vec)

class TestVector(TestCase):
  @skip('not fully implemented yet')
  def test_vector_constructor_succeed(self):
    cases = [
    ]
    for args, x, y in cases:
      with self.subTest(args = args):
        v = g.Vector(*args)
        self.assertEqual(type(v), g.Vector)
        self.assertEqual(v.x, x)
        self.assertEqual(v.y, y)

  @skip('not fully implemented yet')
  def test_vector_constructor_fail(self):
    cases = [
    ]
    for args, ex in cases:
      with self.subTest(args = args):
        self.assertRaises(ex, g.Vector, *args)

  @skip('not fully implemented yet')
  def test_vector_equality_and_hash(self):
    cases = [
    ]
    for a, b, result in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a == b, result)
        self.assertEqual(b == a, result)
        if result:
          self.assertEqual(hash(a), hash(b))

  @skip('not fully implemented yet')
  def test_negation(self):
    cases = [
    ]
    for v, r in cases:
      with self.subTest(vec = v):
        self.assertEqual(-v, r)
        self.assertEqual(v, -r)

  @skip('not fully implemented yet')
  def test_addition(self):
    cases = [
    ]
    zero = Vector(0, 0)
    for a, b, r in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a + b, r)
        self.assertEqual(b + a, r)
        self.assertEqual(a + zero, a)
        self.assertEqual(b + zero, b)
        self.assertEqual(zero + a, a)
        self.assertEqual(zero + b, b)

  @skip('not fully implemented yet')
  def test_subtraction(self):
    cases = [
    ]
    zero = Vector(0, 0)
    for a, b, r in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a - b, r)
        self.assertEqual(b - a, -r)
        self.assertEqual(a - zero, a)
        self.assertEqual(b - zero, b)
        self.assertEqual(zero - a, -a)
        self.assertEqual(zero - b, -b)

  @skip('not fully implemented yet')
  def test_scalar_multiplication(self):
    cases = [
    ]
    zero = Vector(0, 0)
    for a, b, r in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a * b, r)
        self.assertEqual(b * a, r)
        self.assertEqual(0 * b, zero)
        self.assertEqual(1 * b, b)

  @skip('not fully implemented yet')
  def test_transform(self):
    cases = [
    ]
    for vec, trans, r in cases:
      with self.subTest(vec = vec, trans = trans):
        self.assertEqual(vec.transform(trans), r)
        self.assertEqual(trans @ vec, r)

  @skip('not fully implemented yet')
  def test_rotate(self):
    cases = [
    ]
    for vec, theta, result in cases:
      with self.subTest(vec = vec, theta = theta):
        self.assertEqual(vec.rotate(theta), result)

  @skip('not fully implemented yet')
  def test_inner_product(self):
    cases = [
    ]
    for a, b, r in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a | b, r)
        self.assertEqual(b | a, r)
        self.assertEqual((-a) | b, -r)
        self.assertEqual(a | (-b), -r)
        self.assertEqual((3*a) | b, 3*r)

  @skip('not fully implemented yet')
  def test_cross_product(self):
    cases = [
    ]
    for a, b, r in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a ^ b, r)
        self.assertEqual(b ^ a, -r)
        self.assertEqual((-a) ^ b, -r)
        self.assertEqual(a ^ (-b), -r)
        self.assertEqual((3*a) ^ b, 3*r)

class TestAffineTransform(TestCase):
  @skip('not fully implemented yet')
  def test_transform_constructor_succeed(self):
    cases = [
    ]
    for args, a, b, c, d, e, f in cases:
      with self.subTest(args = args):
        trans = g.AffineTransform(*args)
        self.assertEqual(type(trans), g.AffineTransform)
        self.assertEqual(trans.a, a)
        self.assertEqual(trans.b, b)
        self.assertEqual(trans.c, c)
        self.assertEqual(trans.d, d)
        self.assertEqual(trans.e, e)
        self.assertEqual(trans.f, f)

  @skip('not fully implemented yet')
  def test_transform_constructor_fail(self):
    cases = [
    ]
    for args, ex in cases:
      with self.subTest(args = args):
        self.assertRaises(ex, g.AffineTransform, *args)

  @skip('not fully implemented yet')
  def test_transform(self):
    cases = [
    ]
    for t1, t2, t3 in cases:
      with self.subTest(t1 = t1, t2 = t2):
        self.assertEqual(t1.transform(t2), t3)
        self.assertEqual(t2 @ t1, t3)
        self.assertEqual(t1.transform(g.identity_transform), t1)
        self.assertEqual(t2.transform(g.identity_transform), t2)
        self.assertEqual(g.identity_transform.transform(t1), t1)
        self.assertEqual(g.identity_transform.transform(t2), t2)

  @skip('not fully implemented yet')
  def test_negation(self):
    cases = [
    ]
    for trans, result in cases:
      with self.subTest(trans = trans):
        self.assertEqual(-trans, result)
        self.assertEqual(trans, -result)

  @skip('not fully implemented yet')
  def test_determinant(self):
    cases = [
    ]
    for trans, det in cases:
      with self.subTest(trans = trans):
        self.assertEqual(trans.det(), det)
        self.assertEqual(trans.det(), det)    # sanity check for memoization
        self.assertEqual((-trans).det(), det)

  @skip('not fully implemented yet')
  def test_is_orientation_preserving(self):
    cases = [
    ]
    for trans, result in cases:
      with self.subTest(trans = trans):
        self.assertEqual(trans.is_orientation_preserving(), result)
        self.assertEqual(trans.is_orientation_preserving(), result)

  @skip('not fully implemented yet')
  def test_is_conformal(self):
    cases = [
    ]
    for trans, result in cases:
      with self.subTest(trans = trans):
        self.assertEqual(trans.is_conformal(), result)
        self.assertEqual(trans.is_conformal(), result)

class TestTransformFunctions(TestCase):
  @skip('not fully implemented yet')
  def test_identity_transform(self):
    cases = [
    ]
    identity = g.identity_transform
    for c in cases:
      with self.subTest(trans = trans):
        self.assertEqual(c.transform(identity), c)
        self.assertEqual(identity @ c, c)

  @skip('not fully implemented yet')
  def test_rotation(self):
    cases = [
    ]
    for theta, x, r in cases:
      with self.subTest(x = x, theta = theta):
        self.assertEqual(x.transform(g.rotation(theta)), r)
        self.assertEqual(x, r.transform(g.rotation(-theta)))

  @skip('not fully implemented yet')
  def test_scaling(self):
    cases = [
    ]
    for args, x, r in cases:
      with self.subTest(x = x, args = args):
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
        self.assertEqual(rect.bbox(), bbox)

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
  _test_polygons = {}

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
