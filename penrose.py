'''A module to work with the Penrose tilings P2 (kites and darts) and P3 (rhombs)'''

# MIT-licensed; see LICENSE for details

from fractions import Fraction as Q
from pen_num import Number as Y, phi, inv_phi
import pen_geom as pg
from pen_geom import Point, Vector, AffineTransform, Polygon, LineSegment
import itertools as it

class TileWithMatchingRule:
  def __init__(self):
    self.__bbox = None
    self.__hash = None
    self.__edges = None

  def vertices(self):
    '''Returns the list of n vertices for the tile,
    with the i'th edge being from vertex i to vertex (i+1)%n.

    The tile is assumed to be simply-connected, with the vertices
    listed going counterclockwise around the tile exterior.'''
    raise NotImplementedError

  def matching_rules(self):
    '''Returns the (oriented) matching rule for the n edges as integers,
    with a negative integer -i representing rule i in the opposite direction.

    The IDs for the matching rules are assumed to be globally-unique, so
    any two instances of TileWithMatchingRule may have their rules compared.'''
    raise NotImplementedError

  def decompose(self, decomp_id):
    '''If decomp_id is recognized, returns a list or tuple of tiles
    representing a decomposition of self of type decomp_id; if
    decomp_id is not recognized, returns None'''
    return None

  def tile_set(self):
    '''Returns an ID indicating the tile set this tile belongs to.'''
    raise NotImplementedError

  def convex_decomposition(self):
    '''Returns an iterable of Polygons such that
    (1) each polygon is convex and
    (2) the union of the *interiors* of the polygons is point-for-point
    equal to the interior of the tile'''
    raise NotImplementedError

  def bbox(self):
    '''Returns a Rectangle that contains the entirety of the tile.'''
    if self.__bbox is not None:
      return self.__bbox
    bb = Polygon(self.vertices()).bbox()
    self.__bbox = bb
    return bb

  def _edges(self):
    e = self.__edges
    if e is None:
      v = self.vertices()
      n = len(v)
      e = tuple(LineSegment(v[i], v[(i+1)%n]) for i in range(n))
      self.__edges = e
    return e

  def matches(self, other):
    '''Returns True if the tiles don't overlap or if they overlap at
    an edge and the matching rules match, or False otherwise.'''
    if not isinstance(other, TileWithMatchingRule):
      raise TypeError

    if not pg.do_bboxes_overlap(self.bbox(), other.bbox()): # fast check
      return True

    edges_possibly_meet = False

    for poly_s in self.convex_decomposition():
      for poly_o in other.convex_decomposition():
        result = pg.do_convex_polygons_intersect(poly_s, poly_o)
        if result[0]: # overlap
          if result[1]: # overlap of non-zero area
            return False
          edge_indices = result[2]
          if edge_indices is not None: # edge overlap in decomposed polygons
            edges_possibly_meet = True

    if not edges_possibly_meet:
      return True

    # So, if we get here, there's overlap between the two tiles,
    # but of zero area. Let's see what overlap (if any) is edge-to-edge:

    edges_s, edges_o = self._edges(), other._edges()
    mr_s, mr_o = self.matching_rules(), other.matching_rules()

    for i, e_s in zip(it.count(), edges_s):
      for j, e_o in zip(it.count(), edges_o):
        if e_s.significantly_overlaps_with(e_o):
          # If e_s and e_o overlap, they *must* have the same endpoints,
          # and have matching rules that are negatives of each other.
          # Since both sets of vertices are enumerated in CCW order,
          # if the endpoints are the same, they'll be in opposite order in
          # self and other.
          if e_s.begin != e_o.end or e_s.end != e_o.begin or mr_s[i] != -mr_o[j]:
            return False
          # No other e_o will overlap e_s, so we can skip the rest of the innermost loop:
          break

    # If we get *here*, all edge pairs that overlap matched successfully:
    return True

  def __str__(self):
    ts, v, mr = self.tile_set(), self.vertices(), self.matching_rules()
    ty = type(self)
    details = '\n'.join( '  {}...{}...'.format(v[i], mr[i]) for i in range(len(v)) )
    return '<{}.{} (tile_set={})\n{}close\n>'.format(ty.__module__, ty.__name__, ts, details)

  def __eq__(self, other):
    if not isinstance(other, TileWithMatchingRule):
      return NotImplemented
    v,  ov  = self.vertices(),       other.vertices()
    mr, omr = self.matching_rules(), other.matching_rules()
    if (len(v) != len(mr)) or (len(ov) != len(omr)): # sanity check
      raise ValueError
    if (len(v) != len(ov)) or (len(mr) != len(omr)):
      return False
    n = len(v)

    # It's possible that the tiles are equal, but their vertices are enumerated starting
    # at different points. So we need to try possible rotations of relative orders--
    # thank goodness we already require simple-connectedness and CCW vertex order:
    first_pt = v[0]
    for i in range(n):
      if first_pt == ov[i]:
        rot_v  = v[i:]  + v[:i]
        rot_mr = mr[i:] + mr[:i]
        if all(rot_v[j] == ov[j] and rot_mr[j] == omr[j] for j in range(n)):
          return True

    # No rotation matched:
    return False

  def __hash__(self):
    if self.__hash is None:
      v = self.vertices()
      mr = self.matching_rules()

      # Disambiguate the ordering of vertices/edges by starting
      # at the lexicographically-earliest one
      indexed_v = [(v[i].x, v[i].y, i) for i in range(len(v))]
      idx_of_min = min(indexed_v)[2]
      v  = tuple(v[idx_of_min:])  + tuple(v[:idx_of_min])
      mr = tuple(mr[idx_of_min:]) + tuple(mr[:idx_of_min])

      self.__hash = hash(v) ^ hash(mr)

    return self.__hash

class TransformableTile(TileWithMatchingRule):
  def __init__(self, t = pg.identity_transform):
    '''Constructs a proto-tile, transformed by affine transform t.
    
    The transform t must be orientation-preserving and angle-preserving.'''

    if (not isinstance(t, AffineTransform)):
      raise TypeError
    if not (t.is_orientation_preserving() and t.is_conformal()):
      raise ValueError

    super().__init__()
    self._v = tuple(pt.transform(t) for pt in self._proto_vertices)
    if self._convex_decomposition is None:
      self._convex = (Polygon(self._v),)
    else:
      addl = tuple(pt.transform(t) for pt in self._additional_proto_points)
      self._convex = tuple(
        Polygon((self._v[i] if i >= 0 else addl[-i-1]) for i in idxs)
        for idxs in self._convex_decomposition
      )
    self._t = t

  _additional_proto_points = ()

  _convex_decomposition = None

  _decompositions = {}

  def vertices(self):
    return self._v

  def matching_rules(self):
    return self._matching_rules

  def decompose(self, decomp_id):
    decomp_prototiles = self._decompositions.get(decomp_id, None)
    if decomp_prototiles is None:
      return None

    return [pt.transform(self._t) for pt in decomp_prototiles]

  def tile_set(self):
    return self._tile_set

  def convex_decomposition(self):
    return self._convex

  def transform(self, t):
    return type(self)(t @ self._t)

  def rotate(self, n):
    return self.transform(pg.rotation(n))

  def translate(self, dx, dy=None):
    return self.transform(pg.translation(dx, dy))

  def scale(self, scl):
    return self.transform(pg.scaling(scl))

  def curr_transform(self):
    return self._t

_origin = Point(0, 0)
_one_x = Point(1, 0)
_thick_diag = Vector(1, 0).rotate(4)
_thin_diag = Vector(1, 0).rotate(2)

# Coordinates for a {kite,dart} of long side-length 1,
# going counter-clockwise around the shape
proto_kite = (_origin, _one_x, _one_x.rotate(2), _one_x.rotate(4))
proto_dart = (_origin, _one_x, Point(inv_phi, 0).rotate(2), _one_x.rotate(4))

# Similarly, but for the {thick,thin} rhombs
proto_thick = (_origin, _one_x, _one_x + _thick_diag, _origin + _thick_diag)
proto_thin  = (_origin, _one_x, _one_x + _thin_diag,  _origin + _thin_diag)

# Matching rules for these tiles' edges:
_match_kite = (2, 1, -1, -2)
_match_dart = (-2, -1, 1, 2)
_match_thick = (3, 4, -4, -3)
_match_thin = (3, -3, 4, -4)

class KiteTile(TransformableTile):
  _proto_vertices = proto_kite
  _matching_rules = _match_kite
  # Already convex (as are {Thick,Thin}Rhomb), so no need to specify decomposition
  _decompositions = {}
  _tile_set = 'P2'

# A point on the dart tile's edge that we can use to reduce it into two
# triangles with the needed overlap for the convex-polygon decomposition
_dart_aux_point = _one_x + (Vector(1, 0).rotate(8))

class DartTile(TransformableTile):
  _proto_vertices = proto_dart
  _matching_rules = _match_dart
  _additional_proto_points = (_dart_aux_point,)
  _convex_decomposition = ((0, 1, -1), (0, 2, 3))
  _decompositions = {}
  _tile_set = 'P2'

class ThickRhomb(TransformableTile):
  _proto_vertices = proto_thick
  _matching_rules = _match_thick
  _decompositions = {}
  _tile_set = 'P3'

class ThinRhomb(TransformableTile):
  _proto_vertices = proto_thin
  _matching_rules = _match_thin
  _decompositions = {}
  _tile_set = 'P3'

# Robinson's A- and B- tiles; coordinates chosen to make
# conversions between P2 <-> A and P3 <-> B easy
class A_K1(TransformableTile):
  _proto_vertices = (proto_kite[0], proto_kite[1], proto_kite[2])
  _matching_rules = (42, 41, 43)
  _decompositions = {}
  _tile_set = 'Robinson A'

class A_K2(TransformableTile):
  _proto_vertices = (proto_kite[0], proto_kite[2], proto_kite[3])
  _matching_rules = (-43, -41, -42)
  _decompositions = {}
  _tile_set = 'Robinson A'

class A_D1(TransformableTile):
  _proto_vertices = (proto_dart[0], proto_dart[1], proto_dart[2])
  _matching_rules = (-42, -41, -44)
  _decompositions = {}
  _tile_set = 'Robinson A'

class A_D2(TransformableTile):
  _proto_vertices = (proto_dart[0], proto_dart[2], proto_dart[3])
  _matching_rules = (44, 41, 42)
  _decompositions = {}
  _tile_set = 'Robinson A'

class B_L1(TransformableTile):
  _proto_vertices = (proto_thick[0], proto_thick[1], proto_thick[2])
  _matching_rules = (51, 52, 53)
  _decompositions = {}
  _tile_set = 'Robinson B'

class B_L2(TransformableTile):
  _proto_vertices = (proto_thick[0], proto_thick[2], proto_thick[3])
  _matching_rules = (-53, -52, -51)
  _decompositions = {}
  _tile_set = 'Robinson B'

class B_S1(TransformableTile):
  _proto_vertices = (proto_thin[0], proto_thin[1], proto_thin[3])
  _matching_rules = (51, 54, -52)
  _decompositions = {}
  _tile_set = 'Robinson B'

class B_S2(TransformableTile):
  _proto_vertices = (proto_thin[1], proto_thin[2], proto_thin[3])
  _matching_rules = (-51, 52, -54)
  _decompositions = {}
  _tile_set = 'Robinson B'

KiteTile._decompositions['to-A'] = (A_K1(), A_K2())
DartTile._decompositions['to-A'] = (A_D1(), A_D2())

ThickRhomb._decompositions['to-B'] = (B_L1(), B_L2())
ThinRhomb._decompositions['to-B']  = (B_S1(), B_S2())

A_K1._decompositions['to-P2'] = (KiteTile(),)
A_K2._decompositions['to-P2'] = (KiteTile(),)
A_D1._decompositions['to-P2'] = (DartTile(),)
A_D2._decompositions['to-P2'] = (DartTile(),)

B_L1._decompositions['to-P3'] = (ThickRhomb(),)
B_L2._decompositions['to-P3'] = (ThickRhomb(),)
B_S1._decompositions['to-P3'] = (ThinRhomb(),)
B_S2._decompositions['to-P3'] = (ThinRhomb(),)

A_K1._decompositions['half-deflation'] = (
  B_L1(pg.translation(1,0) @ pg.rotation(8) @ pg.scaling(inv_phi)),
  B_S2(pg.translation(1,0) @ pg.rotation(-4) @ pg.scaling(inv_phi) @ pg.translation(-Vector(proto_thin[2]))),
)
A_K2._decompositions['half-deflation'] = (
  B_L2(pg.rotation(-8) @ pg.scaling(inv_phi) @ pg.translation(-Vector(proto_thick[2]))),
  B_S1(pg.translation(Vector(proto_kite[3])) @ pg.rotation(-4) @ pg.scaling(inv_phi)),
)
A_D1._decompositions['half-deflation'] = (
  B_L2(pg.rotation(-2) @ pg.scaling(inv_phi)),
)
A_D2._decompositions['half-deflation'] = (
  B_L1(pg.rotation(2) @ pg.scaling(inv_phi)),
)

B_L1._decompositions['half-deflation'] = (
  A_K2(pg.rotation(-2)),
  A_D2(pg.translation(Vector(proto_thick[2])) @ pg.rotation(10)),
)
B_L2._decompositions['half-deflation'] = (
  A_K1(pg.rotation(2)),
  A_D1(pg.translation(Vector(proto_thick[2])) @ pg.rotation(10)),
)
B_S1._decompositions['half-deflation'] = (
  A_K2(pg.rotation(-2)),
)
B_S2._decompositions['half-deflation'] = (
  A_K1(pg.translation(Vector(proto_thin[2])) @ pg.rotation(10)),
)

def _mk_full_deflations():
  for T in (A_K1, A_K2, A_D1, A_D2, B_L1, B_L2, B_S1, B_S2):
    tile = T()
    hd = tile.decompose('half-deflation')
    T._decompositions['deflation'] = tuple(it.chain( *(tt.decompose('half-deflation') for tt in hd) ))

_mk_full_deflations()
