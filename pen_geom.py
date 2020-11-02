'''Geometric objects and manipulations using the number field pen_num.Number'''

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

  def as_offset_vector(self):
    return Vector(self)

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
identity_transform = AffineTransform(1, 0, 0, 0, 1, 0)

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
      if begin == end:
        raise ValueError
      self.begin, self.end, self.direction = begin, end, end - begin
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
    if len(vertices) == 1 and _is_iterable(vertices[0]):
      vertices = list(vertices[0])
    if not all(isinstance(pt, Point) for pt in vertices):
      raise TypeError
    if len(vertices) < 3: # polygon needs at least three vertices
      raise ValueError

    self._v = tuple(vertices)
    self._e, self._is_convex, self._bbox = None, None, None

  def vertices(self):
    return self._v

  def edges(self):
    if self._e is None:
      v = self._v
      l = len(v)
      self._e = tuple(LineSegment(v[i], v[(i+1)%l]) for i in range(l))
    return self._e

  def is_convex(self):
    if self._is_convex is None:
      raise NotImplementedError
      # A simply-connected polygon is convex iff all its interior angles are
      # less than or equal to 180 degrees, which in turn is the case iff
      # the polygon always "turns" the same direction (left or right) at
      # every vertex.
      # We don't support vertices within straight-line segments, so we don't
      # have to worry about the 180 degree condition, so:
      edges = self._e
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
      max_y = min(pt.y for pt in v)
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

# Helper function; returns -1 is pt lies directly below the segment (r, s),
# 0 if pt is exactly on (r, s), and +1 otherwise.
def _on_or_below(pt, r, s):
  if r.x < s.x:
    r, s = s, r
  if (pt.x < s.x) or (pt.x >= r.x):
    return 1
  return ((s-r) ^ (pt-r)).sgn()

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
  edge_normals     = [e.direction.transform(_rot90) for e in A.edges()]
  edge_normals.extend(e.direction.transform(_rot90) for e in B.edges())

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

  for i in range(2):
    for n in edge_normals:
      proj_A = [n | v for v in A_v]
      proj_B = [n | v for v in B_v]
      min_A, max_A = min(proj_A), max(proj_A)
      min_B, max_B = min(proj_B), max(proj_B)

      # Is no overlap between [min_A, max_A] and [min_B, max_B] for some n,
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
      # Find the orientations of all endpoints w.r.t. the other edge:
      dir_a, dir_b = ea.direction, eb.direction
      orient = [
        (dir_a ^ (eb.begin - ea.begin)).sgn(),
        (dir_a ^ (eb.end   - ea.begin)).sgn(),
        (dir_b ^ (ea.begin - eb.begin)).sgn(),
        (dir_b ^ (ea.begin - eb.begin)).sgn()
      ]
      if all(s == 0 for s in orient): # If all four points are collinear
        coord_a, coord_b = sorted([ea.begin.x, ea.end.x]), sorted([eb.begin.x, eb.end.x])
        if (ea.begin.x == ea.end.x): # handle special case of vertical lines
          coord_a, coord_b = sorted([ea.begin.y, ea.end.y]), sorted([eb.begin.y, eb.end.y])
        if (coord_a[0] < coord_b[1]) and (coord_b[0] < coord_a[1]):
          # We have overlap of lines that's more than just a single point!
          return (True, False, (i, j))

  # If we get here, no two edges meet at more than just a point:
  return (True, False, None)
