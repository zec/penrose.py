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
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_rotation(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_scaling(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_translation(self):
    cases = [
    ]
    raise NotImplementedError

class TestLineSegment(TestCase):
  @skip('not fully implemented yet')
  def test_constructor_succeed(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_constructor_fail(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_equality(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_addition(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_transform(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_bbox(self):
    cases = [
    ]
    raise NotImplementedError

class TestRectangle(TestCase):
  @skip('not fully implemented yet')
  def test_constructor_succeed(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_constructor_fail(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_equality(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_bbox(self):
    cases = [
    ]
    raise NotImplementedError

class TestDoBboxesOverlap(TestCase):
  @skip('not fully implemented yet')
  def test_do_bboxes_overlap(self):
    cases = [
    ]
    raise NotImplementedError

class TestPolygon(TestCase):
  @skip('not fully implemented yet')
  def test_constructor_succeed(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_constructor_fail(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_vertices(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_edges(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_is_convex(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_bbox(self):
    cases = [
    ]
    raise NotImplementedError

class TestPolygonAlgorithms(TestCase):
  @skip('not fully implemented yet')
  def test_point_in_polygon(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_do_convex_polygons_intersect(self):
    cases = [
    ]
    raise NotImplementedError

  @skip('not fully implemented yet')
  def test_do_convex_polygons_intersect_exceptions(self):
    cases = [
    ]
    raise NotImplementedError
