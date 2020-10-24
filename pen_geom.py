'''Geometric objects and manipulations using the number field pen_num.Number'''

from fractions import Fraction as Q
import pen_num
from pen_num import Number as Y

# Some useful trigonometric constants: sin and cos of 18 degrees,
# and multiples thereof
cos18 = Y(0, Q(1,4), 0, 0)
sin18 = Y(Q(-3,2), 0, Q(1,8), 0)

def _rotation(pt, cos_sin):
  '''Rotate the pair-representing-a-point pt
  by the angle whose cosine and sine are in cos_sin'''

  x, y = pt
  c, s = cos_sin
  return (c * x - s * y, s * x + c * y)

_trig_multiples_of_18 = []

def _populate_mul18():
  cos_sin = (Y(1), Y(0)) # cos and sin of 0 degrees
  for i in range(20):
    _trig_multiples_of_18.append(cos_sin)
    cos_sin = _rotation(cos_sin, (cos18, sin18))

_populate_mul18()

class Point:
  def __init__(x, y = None):

class AffTransform:
  def __init__(self, a, b = None, c = None, d = None, e = None, f = None):
    '''If a is an AffTransform, this works as a copy constructor.
    If a through f are pen_num.Number instances (or castable to such),
    construct the affine transformation that takes (x, y) to
    (a*x + b*y + d, c*x + d*y + f)'''

    if isinstance(a, AffTransform):
      self.a, self.b, self.c, self.d, self.e, self.f =
         a.a,    a.b,    a.c,    a.d,    a.e,    a.f
    elif all([x is not None for x in [a,b,c,d,e,f]]):
      self.a, self.b, self.c, self.d, self.e, self.f =
        Y(a),   Y(b),   Y(c),   Y(d),   Y(e),   Y(f)
    else:
      raise TypeError



