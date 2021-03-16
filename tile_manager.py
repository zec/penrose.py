# MIT-licensed; see LICENSE for details

import penrose as p, pen_num as pn, pen_geom as pg
from collections import defaultdict
from math import floor, ceil

class _TileAlreadyPresent:
  def __str__(self):
    return 'TileAlreadyPresent'

  def __bool__(self):
    return True

TileAlreadyPresent = _TileAlreadyPresent()

class TileManager:
  def __init__(self):
    self._scale_factor = None
    self._tiles = set()
    self._tiles_in_grid = defaultdict(set)
    self._vertices = defaultdict(set)

  def _grid_bounds(self, t):
    bb = t.bbox()
    sf = self._scale_factor
    min_x, max_x = floor(bb.min_x * sf), floor(bb.max_x * sf)
    min_y, max_y = floor(bb.min_y * sf), floor(bb.max_x * sf)
    return (min_x, max_x, min_y, max_y)

  def can_add_tile(self, t):
    if not isinstance(t, p.TileWithMatchingRule):
      raise TypeError
    if len(self._tiles) == 0:
      return True
    if t in self._tiles:
      return TileAlreadyPresent

    # Get all tiles in self with overlapping bboxes
    nearby_tiles = set()

    min_x, max_x, min_y, max_y = self._grid_bounds(t)
    tig = self._tiles_in_grid

    for ix in range(min_x, max_x+1):
      for iy in range(min_y, max_y+1):
        nearby_tiles |= tig[(ix,iy)]

    # Now, make sure the new tile is compatible with existing tiles:
    for nt in nearby_tiles:
      if not t.matches(nt):
        return False

    # If we get here, all nearby tiles are consistent with adding t
    # to the tiling:
    return True

  def try_add_tile(self, t):
    x = self.can_add_tile(t)
    if x is True:
      self._tiles.add(t)

      # Set up our scale factor, if needed:
      if self._scale_factor is None:
        if isinstance(t, p.TransformableTile):
          self._scale_factor = pn.approx_inv_sqrt(t.curr_transform().det())
        else:
          bb = t.bbox()
          isqrt = pn.approx_inv_sqrt(min(bb.max_x - bb.min_x, bb.max_y - bb.min_y))
          self._scale_factor = isqrt * isqrt

      min_x, max_x, min_y, max_y = self._grid_bounds(t)
      tig = self._tiles_in_grid

      for ix in range(min_x, max_x+1):
        for iy in range(min_y, max_y+1):
          tig[(ix,iy)].add(t)

      verts = self._vertices
      for v in t.vertices():
        verts[v].add(t)

    return x

  def add_tile(self, t):
    if not self.try_add_tile(t):
      raise ValueError

  def remove_tile(self, t):
    if t not in self._tiles:
      return

    self._tiles.remove(t)

    min_x, max_x, min_y, max_y = self._grid_bounds(t)
    tig = self._tiles_in_grid
    for ix in range(min_x, max_x+1):
      for iy in range(min_y, max_y+1):
        tix[(ix,iy)].remove(t)

    verts = self._vertices
    for v in t.vertices():
      verts[v].remove(t)

  def get_tiles(self):
    return list(self._tiles)

  def get_vertices(self):
    verts = self._vertices
    return [v for v in verts.keys() if len(verts[v]) != 0]

  def transform(self, trns):
    new_tm = TileManager()
    for t in self._tiles:
      new_tm.add_tile(t.transform(trns))
    return new_tm

  def decompose(self, decomp_id):
    new_tm = TileManager()
    for t in self._tiles:
      for nt in t.decompose(decomp_id):
        new_tm.add_tile(nt)
    return new_tm

  def bbox(self):
    if len(self._tiles) == 0:
      return None

    bboxes = [t.bbox() for t in self._tiles]
    min_x = min(bb.min_x for bb in bboxes)
    max_x = max(bb.max_x for bb in bboxes)
    min_y = min(bb.min_y for bb in bboxes)
    max_y = max(bb.max_y for bb in bboxes)
    return pg.Rectangle(min_x, min_y, max_x, max_y)
