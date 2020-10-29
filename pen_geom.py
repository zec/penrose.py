'''Geometric objects and manipulations using the number field pen_num.Number'''

from fractions import Fraction as Q
import pen_num
from pen_num import Number as Y

# Some useful trigonometric constants: sin and cos of 18 degrees,
# and of angles that are multiples thereof
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
  '''A point on the two-dimensional Euclidean plane'''

  def __init__(self, x, y = None):
    if isinstance(x, Point):
      self.x, self.y = x.x, x.y
    elif (x is not None) and (y is not None):
      self.x, self.y = Y(x), Y(y)
    else:
      raise TypeError

  def __repr__(self):
    return 'Point(x={}, y={})'.format(repr(self.x), repr(self.y))

  def __str__(self):
    return '<Point ({a.x}, {a.y})>'.format(a=self)

  def __eq__(self, other):
    if not isinstance(other, Point):
      return NotImplemented
    return (self.x == other.x) and (self.y == other.y)

  def __hash__(self):
    return hash((0, self.x, self.y))

  def transform(self, t):
    '''Returns self transformed by affine tranformation t'''

    if not isinstance(t, AffineTransform):
      raise TypeError
    x, y = self.x, self.y
    return Point(t.a * x + t.b * y + t.c, t.d * x + t.e * y + t.f)

  def __rmatmul__(self, t):
    if not isinstance(t, AffineTransform):
      return NotImplemented
    return self.transform(t)

  def __sub__(self, other):
    if not isinstance(other, Point):
      return NotImplemented
    return Vector(self.x - other.x, self.y - other.y)

  def translate(self, x, y = None):
    if isinstance(x, Vector):
      x, y = x.x, x.y
    elif (x is not None) and (y is not None):
      x, y = Y(x), Y(y)
    else:
      raise TypeError

    return Point(self.x + x, self.y + y)

  def rotate(self, theta):
    return self.transform(rotation(theta))

  def bbox(self):
    return Rectangle(self, self)

class Vector:
  '''An offset in the two-dimensional Euclidean plane'''

  def __init__(self, x, y = None):
    if isinstance(x, Point) and (y is None):
      self.x, self.y = x.x, x.y
    elif (x is not None) and (y is not None):
      self.x, self.y = Y(x), Y(y)
    else:
      raise TypeError

  def __repr__(self):
    return 'Vector(x={}, y={})'.format(repr(self.x), repr(self.y))

  def __str__(self):
    return '<Vector ({a.x}, {a.y})>'.format(a=self)

  def __eq__(self, other):
    if not isinstance(other, Vector):
      return NotImplemented
    return (self.x == other.x) and (self.y == other.y)

  def __hash__(self):
    return hash((1, self.x, self.y))

  def __neg__(self):
    return Vector(-self.x, -self.y)

  def _do_addition(self, other):
    if isinstance(other, Vector):
      return Vector(self.x + other.x, self.y + other.y)
    elif isinstance(other, Point):
      return Point(self.x + other.x, self.y + other.y)
    elif isinstance(other, AffineTransform):
      return other.transform(translation(self))
    else:
      return NotImplemented

  def __add__(self, other):
    return self._do_addition(other)

  def __radd__(self, other):
    return self._do_addition(other)

  def __sub__(self, other):
    return self._do_addition(self, -other)

  def __rsub__(self, other):
    return (-self)._do_addition(other)

  def _do_multiplication(self, other):
    try:
      other = Y(other)
    except:
      return NotImplemented
    return Vector(other * self.x, other * self.y)

  def __mul__(self, other):
    return self._do_multiplication(other)

  def __rmul__(self, other):
    return self._do_multiplication(other)

  # Note the difference between here and transforming a Point
  def _do_transform(self, t):
    if not isinstance(t, AffineTransform):
      return NotImplemented
    return Vector(t.a * self.x + t.b * self.y, t.d * self.x + t.e * self.y)

  def transform(self, t):
    x = self._do_transform(t)
    if x is NotImplemented:
      raise TypeError
    return x

  def rotate(self, n):
    return self.transform(rotation(n))

  def __rmatmul__(self, t):
    return self.transform(t)

  def __or__(self, other):
    '''Inner (dot) product of self with other'''

    if not isinstance(other, Vector):
      return NotImplemented
    return self.x * other.x + self.y * other.y

  def __xor__(self, other):
    '''(Scalar) cross product of self with other'''

    if not isinstance(other, Vector):
      return NotImplemented
    return self.x * other.y - self.y * other.x

class AffineTransform:
  def __init__(self, a, b = None, c = None, d = None, e = None, f = None):
    '''If a is an AffineTransform, this works as a copy constructor.
    If a through f are pen_num.Number instances (or castable to such),
    construct the affine transformation that takes (x, y) to
    (a*x + b*y + c, d*x + e*y + f)'''

    if isinstance(a, AffineTransform):
      self.a, self.b, self.c, self.d, self.e, self.f = \
         a.a,    a.b,    a.c,    a.d,    a.e,    a.f
    elif all(x is not None for x in [a,b,c,d,e,f]):
      self.a, self.b, self.c, self.d, self.e, self.f = \
        Y(a),   Y(b),   Y(c),   Y(d),   Y(e),   Y(f)
    else:
      raise TypeError
    self._memoized = {}

  def __repr__(self):
    return 'AffineTransform(a={}, b={}, c={}, d={}, e={}, f={})'.format(
      repr(self.a), repr(self.b), repr(self.c),
      repr(self.d), repr(self.e), repr(self.f)
    )

  def __str__(self):
    return '<AffineTransform a={x.a} b={x.b} c={x.c} d={x.d} e={x.e} f={x.f}>'.format(x=self)

  def transform(self, t):
    '''Returns the composition of self with the affine tranform t'''
    if not isinstance(t, AffineTransform):
      raise TypeError
    return AffineTransform(
      self.a * t.a + self.d * t.b, self.b * t.a + self.e * t.b, self.c * t.a + self.f * t.b + t.c,
      self.a * t.d + self.d * t.e, self.b * t.d + self.e * t.e, self.c * t.d + self.f * t.e + t.f
    )

  def __matmul__(self, t):
    if not isinstance(t, AffineTransform):
      return NotImplemented
    # in math, composition is traditionally performed right-to-left:
    return t.transform(self)

  def __neg__(self):
    return self.transform(scale(-1, -1))

  def _memoize_method(self, key, function):
    if key not in self._memoized:
      self._memoized[key] = function(self)
    return self._memoized[key]

  def det(self):
    '''Returns the determinant of the transform'''
    return self._memoize_method('det', lambda t: t.a * t.e - t.b * t.d)

  def is_orientation_preserving(self):
    '''Returns whether or not the transform keeps clockwise paths clockwise'''
    return self._memoize_method('orient', lambda t: t.det() > 0)

  def is_conformal(self):
    '''Returns whether or not the transform preserves angles'''
    # So, a linear transform is conformal iff it scales all vectors equally, i.e.,
    # for all vectors v, (T @ v) | (T @ v) == c * (v | v) for some constant c.
    # Expanding out that equality in terms of the components of the transform
    # and the vector, that turns out to be equivalent to the following predicate:
    return self._memoize_method(
      'conformal',
      lambda t: (t.a*t.a + t.d*t.d == t.b*t.b + t.e*t.e) and (t.a*t.b == -(t.d*t.e))
    )

# The identity transformation
AffineTransform.identity = AffineTransform(1, 0, 0, 0, 1, 0)

def rotation(n):
  '''Returns the AffineTransform for rotation by n*18 degrees, n integer'''
  c, s = _trig_multiples_of_18[n % 20]
  return AffineTransform(c, -s, 0,    s, c, 0)

def scaling(sx, sy=None):
  '''Returns the AffineTranform for scaling by sx
  (or for scaling by sx in x and sy in y)'''
  if sy is None:
    sy = sx
  return AffineTransform(sx, 0, 0,    0, sy, 0)

def translation(dx, dy = None):
  '''Returns the AffineTransform for translation by (dx,dy)'''
  if isinstance(dx, Vector) and (dy is None):
    dx, dy = dx.x, dx.y
  return AffineTransform(1, 0, dx,    0, 1, dy)

class LineSegment:
  '''An oriented line segment - it has a beginning and an end'''

  def __init__(self, begin, end):
    if isinstance(begin, Point) and isinstance(end, Point):
      self.begin, self.end = begin, end
    else:
      raise TypeError

  def __eq__(self, other):
    if not isinstance(other, LineSegment):
      return NotImplemented
    return (self.begin == other.begin) and (self.end == other.end)

  def _do_addition(self, other):
    if not isinstance(other, Vector):
      return NotImplemented
    return LineSegment(self.begin + other, self.end + other)

  def __add__(self, other):
    return self._do_addition(other)

  def __radd__(self, other):
    return self._do_addition(other)

  def _do_transform(self, t):
    if not isinstance(t, AffineTransform):
      return NotImplemented
    return LineSegment(
      self.begin.transform(t),
      self.end.transform(t)
    )

  def transform(self, t):
    x = self._do_transform(t)
    if x is NotImplemented:
      raise TypeError
    return x

  def __rmatmul__(self, t):
    return self._do_transform(t)

  def bbox(self):
    return Rectangle(self.begin, self.end)

class Rectangle:
  '''A rectangle with sides parallel to the x- and y-axes'''

  def __init__(self, p1, p2, x2=None, y2=None):
    if isinstance(p1, Point) and isinstance(p2, Point):
      self._populate_self(p1, p2)
    elif isinstance(p1, Point) and isinstance(p2, Vector):
      self._populate_self(p1, p1 + p2)
    elif isinstance(p2, Point) and isinstance(p1, Vector):
      self._populate_self(p2, p2 + p1)
    else:
      self._populate_self({x: Y(p1), y: Y(p2)}, {x: Y(x2), y: Y(y2)})

  def _populate_self(self, p1, p2):
    self.min_x, self.max_x = min(p1.x, p2.x), max(p1.x, p2.x)
    self.min_y, self.max_y = min(p1.y, p2.y), max(p1.y, p2.y)

  def __eq__(self, other):
    if not isinstance(other, Rectangle):
      return NotImplemented
    return (self.min_x == other.min_x) and \
           (self.max_x == other.max_x) and \
           (self.min_y == other.min_y) and \
           (self.max_y == other.max_y)

  def bbox(self):
    return self
