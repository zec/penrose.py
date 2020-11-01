import unittest

class PenNumSanityCheck(unittest.TestCase):
  '''Quick way to make sure tests in this module are being run'''
  def test_hello_world(self):
    self.assertEqual(2+2, 4)
