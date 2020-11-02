from unittest import TestCase, skip

class PenGeomSanityCheck(TestCase):
  '''Quick way to make sure tests in this module are being run'''
  def test_hello_world(self):
    self.assertEqual(2+2, 4)

  #def test_error(self):
  #  self.assertTrue(False)

class TestPoint(TestCase):
  @skip('not implemented yet')
  def test_point_constructor_succeed(self):
    pass

  @skip('not implemented yet')
  def test_point_constructor_fail(self):
    pass

  @skip('not implemented yet')
  def test_point_equality_and_hash(self):
    pass

  @skip('not implemented yet')
  def test_transform(self):
    pass

  @skip('not implemented yet')
  def test_subtraction(self):
    pass

  @skip('not implemented yet')
  def test_addition(self):
    pass

  @skip('not implemented yet')
  def test_translate(self):
    pass

  @skip('not implemented yet')
  def test_rotate(self):
    pass

  @skip('not implemented yet')
  def test_bbox(self):
    pass

  @skip('not implemented yet')
  def test_as_offset_vector(self):
    pass
