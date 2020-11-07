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
  @skip('not fully implemented yet')
  def test_point_constructor_succeed(self):
    cases = [
    ]
    for args, x, y in cases:
      with self.subTest(args = args):
        pt = g.Point(*args)
        self.assertEqual(type(pt), g.Point)
        self.assertEqual(pt.x, x)
        self.assertEqual(pt.y, y)

  @skip('not fully implemented yet')
  def test_point_constructor_fail(self):
    cases = [
    ]
    for args, ex in cases:
      with self.subTest(args = args):
        self.assertRaises(ex, g.Point, *args)

  @skip('not fully implemented yet')
  def test_point_equality_and_hash(self):
    cases = [
    ]
    for a, b, result in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a == b, result)
        self.assertEqual(b == a, result)
        self.assertEqual(a != b, not result)
        self.assertEqual(b != a, not result)
        if result:
          self.assertEqual(hash(a), hash(b))

  @skip('not fully implemented yet')
  def test_transform(self):
    cases = [
    ]
    for pt, trans, result in cases:
      with self.subTest(pt = pt, trans = trans):
        self.assertEqual(pt.transform(trans), result)
        self.assertEqual(trans @ pt, result)

  @skip('not fully implemented yet')
  def test_subtraction_succeed(self):
    cases = [
    ]
    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a - b, c)

  @skip('not fully implemented yet')
  def test_subtraction_fail(self):
    cases = [
    ]
    for a, b, ex in cases:
      with self.subTest(a = a, b = b):
        self.assertRaises(ex, (lambda x, y: x - y), a, b)

  @skip('not fully implemented yet')
  def test_addition_succeed(self):
    cases = [
    ]
    for a, b, c in cases:
      with self.subTest(a = a, b = b):
        self.assertEqual(a + b, c)
        self.assertEqual(b + a, c)

  @skip('not fully implemented yet')
  def test_addition_fail(self):
    cases = [
    ]
    for a, b, ex in cases:
      with self.subTest(a = a, b = b):
        self.assertRaises(ex, (lambda x, y: x + y), a, b)
        self.assertRaises(ex, (lambda x, y: x + y), b, a)

  @skip('not fully implemented yet')
  def test_translate(self):
    cases = [
    ]
    for pt, args, result in cases:
      with self.subTest(pt = pt, args = args):
        self.assertEqual(pt.translate(*args), result)

  @skip('not fully implemented yet')
  def test_rotate(self):
    cases = [
    ]
    for pt, theta, result in cases:
      with self.subTest(pt = pt, theta = theta):
        self.assertEqual(pt.rotate(theta), result)

  @skip('not fully implemented yet')
  def test_bbox(self):
    cases = [
    ]
    for x, y, bbox in cases:
      with self.subTest(x = x, y = y):
        self.assertEqual(g.Point(x, y).bbox(), g.Rectangle(x, y, x, y))

  @skip('not fully implemented yet')
  def test_as_offset_vector(self):
    cases = [
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
