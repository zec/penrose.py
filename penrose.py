'''A module to work with the Penrose tilings P2 (kites and darts) and P3 (rhombs)'''

from fractions import Fraction as Q
from pen_num import Number as Y, phi, inv_phi
import pen_geom as pg
from pen_geom import Point, Vector, AffineTransform

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

class TileWithMatchingRule:
  def vertices(self):
    '''Returns the list of n vertices for the tile,
    with the i'th edge being from vertex i to vertex (i+1)%n.
    
    The tile is assumed to be simply-connected, with the vertices
    listed going counter-clockwise around the tile exterior.'''
    raise NotImplementedError

  def matching_rules(self):
    '''Returns the (oriented) matching rule for the n edges as integers,
    with a negative integer -i representing rule i in the opposite direction.
    
    The IDs for the matching rules are assumed to be globally-unique, so
    any two instances of TileWithMatchingRule may have their rules compared.'''
    raise NotImplementedError

  def tile_set(self):
    '''Returns an ID indicating the tile set this tile belongs to.'''
    raise NotImplementedError

  def __str__(self):
    ts, v, mr = self.tile_set(), self.vertices(), self.matching_rules()
    details = '\n'.join( '  {}...{}...'.format(v[i], mr[i]) for i in range(len(v)) )
    return '<{} (tile_set={})\n{}close\n>'.format(type(self).__name__, ts, details)

class TransformableTile(TileWithMatchingRule):
  def __init__(self, t = AffineTransform.identity):
    '''Constructs a proto-tile, transformed by affine transform t.
    
    The transform t must be orientation-preserving and angle-preserving.'''

    if (not isinstance(t, AffineTransform)):
      raise TypeError
    if not (t.is_orientation_preserving() and t.is_conformal()):
      raise ValueError
    self._v = tuple(pt.transform(t) for pt in self._proto_vertices)
    self._t = t

  def vertices(self):
    return self._v

  def matching_rules(self):
    return self._matching_rules

  def tile_set(self):
    return self._tile_set

  def transform(self, t):
    return type(self)(t @ self._t)

  def rotate(self, n):
    return self.transform(pg.rotation(n))

  def translate(self, dx, dy=None):
    return self.transform(pg.translation(dx, dy))

  def scale(self, scl):
    return self.transform(pg.scaling(scl))

_P2 = 2

class KiteTile(TransformableTile):
  _proto_vertices = proto_kite
  _matching_rules = _match_kite
  _tile_set = _P2

class DartTile(TransformableTile):
  _proto_vertices = proto_dart
  _matching_rules = _match_dart
  _tile_set = _P2

_P3 = 3

class ThickRhomb(TransformableTile):
  _proto_vertices = proto_thick
  _matching_rules = _match_thick
  _tile_set = _P3

class ThinRhomb(TransformableTile):
  _proto_vertices = proto_thin
  _matching_rules = _match_thin
  _tile_set = _P3
