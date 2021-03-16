# MIT-licensed; see LICENSE for details

import re, math, itertools, penrose, pen_num
from fractions import Fraction
from pen_geom import Point
from collections import defaultdict

_trim_trailing_re = re.compile(r'\.?0+$')

_cache = {}

class DecimalFormatter:
  def __init__(self, n):
    if not isinstance(n, int):
      return TypeError
    if n < 1:
      return ValueError

    self._fmtstr = '{}.{:0' + str(n) + 'd}'
    self._divisor = 10**n
    self._n = n

  _trim_trailing_re = re.compile(r'\.?0+$')

  def _decimal_approx(self, x):
    global _cache

    y = _cache.get((self._n, x), None)
    if y is None:
      y = math.floor(x * self._divisor)
      _cache[(self._n, x)] = y

    return y

  def _to_decimal_string(self, x):
    global _trim_trailing_re

    divs = self._divisor
    if x >= 0:
      s = self._fmtstr.format(x // divs, x % divs)
    else:
      x = abs(x)
      s = '-' + self._fmtstr.format(x // divs, x % divs)
    return re.sub(_trim_trailing_re, '', s)

  def approx(self, x):
    y = self._decimal_approx(x)
    return self._to_decimal_string(y)

  def approx_delta(self, x1, x2):
    y1 = self._decimal_approx(x1)
    y2 = self._decimal_approx(x2)
    return self._to_decimal_string(y2 - y1)

class UndirectedLineSegment:
  def __init__(self, pt1, pt2):
    if not (isinstance(pt1, Point) and isinstance(pt2, Point)):
      raise TypeError
    if pt1 == pt2:
      raise ValueError
    if (pt1.x, pt1.y) < (pt2.x, pt2.y):
      self.end1, self.end2 = pt1, pt2
    else:
      self.end1, self.end2 = pt2, pt1

  def __eq__(self, other):
    if not isinstance(other, UndirectedLineSegment):
      return NotImplemented
    return self.end1 == other.end1 and self.end2 == other.end2

  def __hash__(self):
    return hash((self.end1, self.end2))

def tiling_to_svg_path(tiling, precision):
  untraversed_lines = set()
  untraversed_lines_at = defaultdict(set)
  remaining_points = dict()
  rp_indices = itertools.count()
  uls = None

  for tile in tiling.get_tiles():
    vertices = tile.vertices()
    for pt1, pt2 in zip(vertices, [*vertices[1:], vertices[0]]):
      uls = UndirectedLineSegment(pt1, pt2)
      untraversed_lines.add(uls)
      untraversed_lines_at[pt1].add(uls)
      untraversed_lines_at[pt2].add(uls)
      remaining_points[pt1] = next(rp_indices)

  def remove_segment(l):
    nonlocal untraversed_lines, untraversed_lines_at, remaining_points
    untraversed_lines.discard(l)
    end1, end2 = l.end1, l.end2
    untraversed_lines_at[end1].discard(l)
    if len(untraversed_lines_at[end1]) == 0:
      del remaining_points[end1]
    untraversed_lines_at[end2].discard(l)
    if len(untraversed_lines_at[end2]) == 0:
      del remaining_points[end2]

  def any_element(s):
    for i in s:
      return i
    return None

  def dist_squared(pt1, pt2):
    dx, dy = pt2.x - pt1.x, pt2.y - pt1.y
    return (dx * dx) + (dy * dy)

  if uls is None:
    return ''

  path = []
  fmt = DecimalFormatter(precision)

  # Add a first line segment
  path.append('M{} {}'.format(
    fmt.approx(uls.end1.x),
    fmt.approx(uls.end1.y)
  ))
  path.append('l{} {}'.format(
    fmt.approx_delta(uls.end1.x, uls.end2.x),
    fmt.approx_delta(uls.end1.y, uls.end2.y)
  ))
  last_pt = uls.end2
  remove_segment(uls)

  # Now add the remaining line segments
  while len(untraversed_lines) > 0:
    next_seg = any_element(untraversed_lines_at[last_pt])

    if next_seg is None:
      # Find nearest point with remaining line segments -
      # using a spatial tree would be asymptotically faster, I know,
      # but I'm looking for quick-to-code-up here.
      d2, idx, next_pt = min((dist_squared(last_pt, p), i, p) for p, i in remaining_points.items())

      path.append('m{} {}'.format(
        fmt.approx_delta(last_pt.x, next_pt.x),
        fmt.approx_delta(last_pt.y, next_pt.y)
      ))
      last_pt, next_seg = next_pt, any_element(untraversed_lines_at[next_pt])

    next_pt = next_seg.end2 if last_pt == next_seg.end1 else next_seg.end1
    path.append('l{} {}'.format(
      fmt.approx_delta(last_pt.x, next_pt.x),
      fmt.approx_delta(last_pt.y, next_pt.y)
    ))

    remove_segment(next_seg)
    last_pt = next_pt

  return ''.join(path)

def tiling_arcs_svg(tiling, precision):
  fmt = DecimalFormatter(precision)
  arc_set1, arc_set2 = [], []
  inv_phi, one_minus_inv_phi = pen_num.inv_phi, 1 - pen_num.inv_phi
  inv_phi2 = pen_num.inv_phi * pen_num.inv_phi
  inv_phi_minus_inv_phi2 = inv_phi - inv_phi2
  half_inv_phi = Fraction(1,2) * inv_phi
  one_minus_half_inv_phi = 1 - half_inv_phi

  # The following code makes exquisite use of what *should* be
  # internal details of the four tile types in question.
  v0 = tiling.get_tiles()[0].vertices()
  rev = v0[1] - v0[0] # "represetative edge vector"
  rev_len_squared = (rev.x * rev.x) + (rev.y * rev.y)
  rev_inv_len = pen_num.Number(pen_num.approx_inv_sqrt(rev_len_squared))
  edge_approx_len = pen_num.approx_inv_sqrt(rev_inv_len * rev_inv_len)

  def make_arcs(second_arc_sense = 0):
    nonlocal arc1_start, arc1_end, rad1, arc_set1
    nonlocal arc2_start, arc2_end, rad2, arc_set2
    nonlocal fmt

    r1, r2 = fmt.approx(rad1), fmt.approx(rad2)

    arc_set1.append('M{} {}'.format(
      fmt.approx(arc1_start.x),
      fmt.approx(arc1_start.y)
    ))
    arc_set1.append('A{} {} 0 0 1 {} {}'.format(
      r1, r1,
      fmt.approx(arc1_end.x),
      fmt.approx(arc1_end.y)
    ))

    arc_set2.append('M{} {}'.format(
      fmt.approx(arc2_start.x),
      fmt.approx(arc2_start.y)
    ))
    arc_set2.append('A{} {} 0 {} 1 {} {}'.format(
      r2, r2,
      second_arc_sense,
      fmt.approx(arc2_end.x),
      fmt.approx(arc2_end.y)
    ))

  for t in tiling.get_tiles():
    ty, vs = type(t), t.vertices()
    if ty is penrose.KiteTile:
      arc1_start = vs[0] + inv_phi * (vs[1]-vs[0])
      arc1_end   = vs[0] + inv_phi * (vs[3]-vs[0])
      rad1 = inv_phi * edge_approx_len

      arc2_start = vs[2] + inv_phi * (vs[3]-vs[2])
      arc2_end   = vs[2] + inv_phi * (vs[1]-vs[2])
      rad2 = inv_phi2 * edge_approx_len

      make_arcs()
    elif ty is penrose.DartTile:
      arc1_start = vs[0] + one_minus_inv_phi * (vs[1]-vs[0])
      arc1_end   = vs[0] + one_minus_inv_phi * (vs[3]-vs[0])
      rad1 = one_minus_inv_phi * edge_approx_len

      arc2_start = vs[2] + one_minus_inv_phi * (vs[3]-vs[2])
      arc2_end   = vs[2] + one_minus_inv_phi * (vs[1]-vs[2])
      rad2 = inv_phi_minus_inv_phi2 * edge_approx_len

      make_arcs(1)
    elif ty is penrose.ThickRhomb:
      arc1_start = vs[0] + one_minus_half_inv_phi * (vs[1]-vs[0])
      arc1_end   = vs[0] + one_minus_half_inv_phi * (vs[3]-vs[0])
      rad1 = one_minus_half_inv_phi * edge_approx_len

      arc2_start = vs[2] + half_inv_phi * (vs[3]-vs[2])
      arc2_end   = vs[2] + half_inv_phi * (vs[1]-vs[2])
      rad2 = half_inv_phi * edge_approx_len

      make_arcs()
    elif ty is penrose.ThinRhomb:
      arc1_start = vs[1] + half_inv_phi * (vs[2]-vs[1])
      arc1_end   = vs[1] + half_inv_phi * (vs[0]-vs[1])
      rad1       = half_inv_phi * edge_approx_len

      arc2_start = vs[3] + half_inv_phi * (vs[0]-vs[3])
      arc2_end   = vs[3] + half_inv_phi * (vs[2]-vs[3])
      rad2       = rad1

      make_arcs()
    else:
      raise ValueError

  return { 'type1': ''.join(arc_set1), 'type2': ''.join(arc_set2) }
