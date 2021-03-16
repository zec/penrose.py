'''Geometric objects and manipulations using the number field pen_num.Number'''

# MIT-licensed; see LICENSE for details

from fractions import Fraction as Q
import pen_num
from pen_num import Number as Y
import itertools

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

_valid_numerical_types = {int, float, Q, Y}

def _is_valid_number(x):
  ty = type(x)
  if ty in _valid_numerical_types:
    return True
  elif ty is str:
    try:
      q = Q(x)
      return True
    except ValueError:
      return False
  return False

class Point:
  '''A point on the two-dimensional Euclidean plane'''

  def __init__(self, x, y = None):
    if isinstance(x, Point) and (y is None):
      self.x, self.y = x.x, x.y
    elif all(_is_valid_number(i) for i in [x,y]):
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
    return hash(self.x) ^ ~hash(self.y)

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
    if isinstance(x, Vector) and (y is None):
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

  def as_offset_vector(self):
    return Vector(self)

class Vector:
  '''An offset in the two-dimensional Euclidean plane'''

  def __init__(self, x, y = None):
    if (isinstance(x, Point) or isinstance(x, Vector)) and (y is None):
      self.x, self.y = x.x, x.y
    elif all(_is_valid_number(i) for i in [x,y]):
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
    return hash(self.x) ^ hash(self.y)

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
    return self._do_addition(-other)

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

    if isinstance(a, AffineTransform) \
       and all(x is None for x in [b,c,d,e,f]):
      self.a, self.b, self.c, self.d, self.e, self.f = \
         a.a,    a.b,    a.c,    a.d,    a.e,    a.f
    elif all(_is_valid_number(x) for x in [a,b,c,d,e,f]):
      self.a, self.b, self.c, self.d, self.e, self.f = \
        Y(a),   Y(b),   Y(c),   Y(d),   Y(e),   Y(f)
    else:
      raise TypeError
    self._memoized = {}

  def _iter(self):
    yield self.a
    yield self.b
    yield self.c
    yield self.d
    yield self.e
    yield self.f

  def __eq__(self, other):
    if not isinstance(other, AffineTransform):
      return NotImplemented
    return all(x == y for x, y in zip(self._iter(), other._iter()))

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
    return self.transform(scaling(-1, -1))

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
identity_transform = AffineTransform(1, 0, 0, 0, 1, 0)

_rotations = [AffineTransform(c, -s, 0,    s, c, 0) for c, s in _trig_multiples_of_18]

def rotation(n):
  '''Returns the AffineTransform for rotation by n*18 degrees, n integer'''
  return _rotations[n % 20]

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
      pass
    elif isinstance(begin, Point) and isinstance(end, Vector):
      begin, end = begin, begin + end
    else:
      raise TypeError

    if begin == end:
      raise ValueError

    self.begin, self.end, self.direction = begin, end, end - begin
    self._min, self._max = (begin, end) if (begin.x, begin.y) < (end.x, end.y) else (end, begin)

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

  def is_along_same_line(self, other):
    return (self.direction ^ other.direction).sgn() == 0 \
           and ((self.begin - other.begin) ^ other.direction).sgn() == 0

  def contains_point(self, other):
    ls_dir = self.direction
    s_min, s_max = self._min, self._max

    if ls_dir.y.sgn() == 0:
      return other.y == s_min.y and s_min.x <= other.x and other.x <= s_max.x
    elif ls_dir.x.sgn() == 0:
      return other.x == s_min.x and s_min.y <= other.y and other.y <= s_max.y
    else:
      return ((other - s_min) ^ ls_dir) == 0 \
             and s_min.x <= other.x and other.x <= s_max.x

  def significantly_overlaps_with(self, other):
    '''Returns whether there's overlap between self and other that's more
    than just a single point.'''

    # Weed out the cases where the two segments aren't along the same line:
    if (self.direction ^ other.direction).sgn() != 0 \
       or ((self.begin - other.begin) ^ other.direction).sgn() != 0:
      return False

    # OK, so they're collinear. Let's see if there's overlap of non-zero length:
    s_min, s_max = self._min,  self._max
    o_min, o_max = other._min, other._max

    if self.direction.x.sgn() == 0:
      return s_min.y < o_max.y and o_min.y < s_max.y
    else:
      return s_min.x < o_max.x and o_min.x < s_max.x

class Rectangle:
  '''A rectangle with sides parallel to the x- and y-axes'''

  def __init__(self, p1, p2, x2=None, y2=None):
    if isinstance(p1, Point) and isinstance(p2, Point):
      pass
    elif isinstance(p1, Point) and isinstance(p2, Vector):
      p2 = p1 + p2
    elif isinstance(p2, Point) and isinstance(p1, Vector):
      p1 = p2 + p1
    elif all(_is_valid_number(i) for i in [p1,p2,x2,y2]):
      self.min_x, self.max_x = (p1, x2) if p1 <= x2 else (x2, p1)
      self.min_y, self.max_y = (p2, y2) if p2 <= y2 else (y2, p2)
      return
    else:
      raise TypeError

    xx1, yy1 = p1.x, p1.y
    xx2, yy2 = p2.x, p2.y
    self.min_x, self.max_x = (xx1, xx2) if xx1 <= xx2 else (xx2, xx1)
    self.min_y, self.max_y = (yy1, yy2) if yy1 <= yy2 else (yy2, yy1)

  def __eq__(self, other):
    if not isinstance(other, Rectangle):
      return NotImplemented
    return (self.min_x == other.min_x) and \
           (self.max_x == other.max_x) and \
           (self.min_y == other.min_y) and \
           (self.max_y == other.max_y)

  def __repr__(self):
    ty = type(self)
    return '{}.Rectangle({}, {}, {}, {})'.format(
      ty.__module__,
      repr(self.min_x), repr(self.min_y),
      repr(self.max_x), repr(self.max_y)
    )

  def __str__(self):
    return '<Rectangle x=[{},{}], y=[{},{}]>'.format(
      self.min_x, self.max_x,
      self.min_y, self.max_y
    )

  def bbox(self):
    return self

def do_bboxes_overlap(a, b):
  '''Returns whether the bounding boxes of a and b overlap.'''
  a, b = a.bbox(), b.bbox()
  return (a.min_x <= b.max_x) and (b.min_x <= a.max_x) and \
         (a.min_y <= b.max_y) and (b.min_y <= a.max_y)

# Using the solution from <https://stackoverflow.com/q/1952464>:
def _is_iterable(i):
  try:
    an_iterator = iter(i)
  except TypeError:
    return False
  return True

# One *very* useful thing to know before going into the below code: the scalar
# cross product of two vectors a ^ b depends on the angle of b (ang(b))
# relative to the angle of a (ang(a)). In particular, if ang(b) is
# n degrees counterclockwise from ang(a),
#
#          { positive if 0 < n < 180,
# a ^ b is { negative if 180 < n < 360,
#          { zero     if n == 0 or n == 180
#
# This means that for a directed line segment with points (begin=A, end=B)
# and point of interest C,
# ((B - A) ^ (C - A)).sgn() tells us which side of AB C is on, relative to
# the vector from A to B.

class Polygon:
  '''A polygon. Assumed to be simple (no self-intersections).
  The set of vertices is assumed to be minimal (no vertices
  whose adjoining edges are parallel).'''

  def __init__(self, *vertices):
    if len(vertices) == 0:
      raise ValueError
    elif len(vertices) == 1 and not isinstance(vertices[0], Point):
      # Try to use as an iterable - if an error is thrown by
      # iter() or list(), then it isn't an iterable
      v = list(iter(vertices[0]))
    else:
      v = vertices

    if not all(isinstance(pt, Point) for pt in v):
      raise TypeError
    if len(v) < 3: # polygon needs at least three vertices
      raise ValueError

    self._v = tuple(v)
    self._e, self._is_convex, self._bbox = None, None, None

  def vertices(self):
    return self._v

  def edges(self):
    if self._e is None:
      v = self._v
      l = len(v)
      self._e = tuple(LineSegment(v[i], v[(i+1)%l]) for i in range(l))
    return self._e

  def transform(self, trans):
    if trans.det() == 0:
      return ValueError
    return Polygon(trans @ pt for pt in self._v)

  def __rmatmul__(self, other):
    if not isinstance(other, AffineTransform):
      return NotImplemented
    return self.transform(other)

  def is_convex(self):
    if self._is_convex is None:
      # A simply-connected polygon is convex iff all its interior angles are
      # less than or equal to 180 degrees, which in turn is the case iff
      # the polygon always "turns" the same direction (left or right) at
      # every vertex.
      # We don't support vertices within straight-line segments, so we don't
      # have to worry about the 180 degree condition, so:
      edges = self.edges()
      sgn_turn = (edges[-1].direction ^ edges[0].direction).sgn()
      if sgn_turn == 0:
        raise ValueError
      self._is_convex = all(
        (edges[i].direction ^ edges[i+1].direction).sgn() == sgn_turn
        for i in range(len(edges) - 1)
      )
    return self._is_convex

  def bbox(self):
    if self._bbox is None:
      v = self._v
      min_x = min(pt.x for pt in v)
      max_x = max(pt.x for pt in v)
      min_y = min(pt.y for pt in v)
      max_y = max(pt.y for pt in v)
      self._bbox = Rectangle(min_x, min_y, max_x, max_y)
    return self._bbox

  def __str__(self):
    return '<{}.{}\n  {}\n>'.format(
      type(self).__module__,
      type(self).__name__,
      '\n  '.join(str(v) for v in self._v)
    )

# This algorithm for determining whether a point is inside a simply-connected
# polygon dates back to at least Shimrat (1962) and Hacker (1962);
# this formulation comes from Jeff Erickson's notes [1].
#
# If we needed to handle more complicated polygons, an algorithm like the one
# in Hormann and Agathos (2001) [2] would be needed.
#
# [1] https://jeffe.cs.illinois.edu/teaching/comptop/2017/chapters/01-simple-polygons.pdf
# [2] https://doi.org/10.1016/S0925-7721(01)00012-8

# Helper function; returns -1 is pt lies directly below the segment-minus-a-point [r, s)
# (except when (r, s) is vertical),
# 0 if pt is exactly on (r, s), and +1 otherwise.
def _on_or_below(pt, r, s):
  if pt == r or pt == s:
    return 0
  if r.x != s.x:  # normal case: non-vertical line
    if r.x > s.x:
      r, s = s, r
    if (pt.x < r.x or pt.x >= s.x):
      return 1
    return ((s-r) ^ (pt-r)).sgn()
  else:           # special case: vertical line
    if pt.x != r.x:
      return 1
    if r.y > s.y:
      r, s = s, r
    return int(not (r.y <= pt.y and pt.y <= s.y))

def point_in_polygon(pt, poly):
  '''Returns whether Point pt is inside (+1), outside (-1) or on the
  boundary (0) of the Polygon poly. Poly is assumed to be simply-connected.'''
  sign = -1
  v = poly.vertices()
  prev_vertex = v[-1]
  for curr_vertex in v:
    sign *= _on_or_below(pt, prev_vertex, curr_vertex)
    prev_vertex = curr_vertex
  # sign is -1 if pt is outside poly, zero is pt is on the boundary of
  # poly, and +1 if pt is inside poly.
  return sign

_rot90 = rotation(5) # Rotation CCW by 90 degrees

def do_convex_polygons_intersect(A, B):
  '''Returns a tuple with the following information about the intersection
  (if any) of Polygons A and B:
  (0) whether there's any intersection at all
  (1) whether the intersection is of non-zero areal measure
  (2) if there's an intersection, but of zero measure, involving
      more than one point, a pair with the indices in A and B of
      the edges involved; None in all other cases.

  A and B must be convex.'''

  if not (isinstance(A, Polygon) and isinstance(B, Polygon)):
    raise TypeError
  if not do_bboxes_overlap(A, B): # fast check
    return (False, False, None)
  if not (A.is_convex() and B.is_convex()):
    raise ValueError

  # We have two convex polygons; as such, we can use a test based on the
  # Separating Axis Theorem (SAT) to determine whether two polygons overlap.

  # get the list of vectors that are normal to each edge in the two polygons
  edge_normals     = {e.direction.transform(_rot90) for e in A.edges()}
  edge_normals.update(e.direction.transform(_rot90) for e in B.edges())

  # The SAT tells us that the two polygons (treated as including the boundary)
  # don't overlap if and only if their projections along one or more of
  # edge_normals don't overlap. So, we project the vertices of A and B along
  # each normal and see whether the line segments representing the span of
  # A and B's projections overlap.
  #
  # Except... we don't even need to figure out the 2-d projection vectors,
  # because it turns out that the (directed, with sign) length of
  # the projection of v along w is directly proportional to v | w,
  # which is nice and quick to compute and compare.

  A_v = [Vector(pt) for pt in A.vertices()]
  B_v = [Vector(pt) for pt in B.vertices()]

  edge_meetings = False

  for n in edge_normals:
    proj_A = [v | n for v in A_v]
    proj_B = [v | n for v in B_v]
    min_A, max_A = min(proj_A), max(proj_A)
    min_B, max_B = min(proj_B), max(proj_B)

    # If no overlap between [min_A, max_A] and [min_B, max_B] for some n,
    # these polygons don't touch anywhere.
    if (max_A < min_B) or (max_B < min_A):
      return (False, False, None)

    if (max_A == min_B) or (max_B == min_A):
      edge_meetings = True

  # If we get here, one of two cases occurs:
  # (1) areal overlap between A and B, in which case there is more than just
  #     single-point contact between all projections of A and B
  # (2) overlap between A and B of measure zero, in which case some vertex of
  #     one polygon is on an edge of the other polygon... and we need to figure
  #     out just how in order to determine whether it's just single-point
  #     contact or non-trivial parts of two edges contacting.
  #
  # The value of edge_meetings distinguishes between the two cases.

  if not edge_meetings: # Areal overlap
    return (True, True, None)

  # So, we have overlap, but of areal measure zero. We want to figure out
  # whether it's just a single vertex just barely touching the other polygon,
  # or whether two edges have lineal overlap. If it's the latter, we also
  # want to know which edges, so we can report the result.
  for i, ea in zip(itertools.count(), A.edges()):
    for j, eb in zip(itertools.count(), B.edges()):
      if ea.significantly_overlaps_with(eb):
        # We have overlap of edges that's more than just a single point!
        return (True, False, (i, j))

  # If we get here, no two edges meet at more than just a point:
  return (True, False, None)

_origin_point = Point(0, 0)

# Very simple implementation of turtle geometry
class MiniTurtle:
  def __init__(self):
    global _origin_point
    self._points = []
    self._curr_pt = _origin_point
    self._angle = 0

  def move_to(self, x, y = None):
    ty = type(x)
    if ty is Point:
      self._points.append(x)
      self._curr_pt = x
    else:
      pt = Point(x, y)
      self._points.append(pt)
      self._curr_pt = pt

  def set_absolute_angle(self, theta):
    self._angle = int(theta)

  def forward(self, length):
    pts = self._points
    curr = self._curr_pt
    if len(pts) == 0:
      pts.append(curr)

    new_pt = curr + Vector(length, 0).rotate(self._angle)
    pts.append(new_pt)
    self._curr_pt = new_pt

  def left(self, theta):
    self._angle += int(theta)

  def right(self, theta):
    self._angle -= int(theta)

  def get_points(self):
    return tuple(self._points)
