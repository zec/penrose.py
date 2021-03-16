#!/usr/bin/env python3

import itertools as it
from fractions import Fraction as Q
import penrose as p
import pen_geom as pg

def tile_to_path_string(t):
  v = t.vertices()
  pre_str = ['M {} {}'.format(float(v[0].x), float(v[0].y))]
  for pt in v[1:]:
    pre_str.append('L {} {}'.format(float(pt.x), float(pt.y)))
  pre_str.append('Z')
  return ' '.join(pre_str)

#print(tile_to_path_string(p.KiteTile()))

def write_decomp_svg(main_tile, decomp_tile, fname):
  bb1 = main_tile.bbox()
  bb2 = decomp_tile.bbox()
  min_x, max_x = min(bb1.min_x, bb2.min_x), max(bb1.max_x, bb2.max_x)
  min_y, max_y = min(bb1.min_y, bb2.min_y), max(bb1.max_y, bb2.max_y)

  width_raw  = max_x - min_x
  height_raw = max_y - min_y

  margin = Q(1,5)
  min_x, max_x = min_x - margin * width_raw , max_x + margin * width_raw
  min_y, max_y = min_y - margin * height_raw, max_y + margin * height_raw

  width, height = max_x - min_x, max_y - min_y
  mwh = min(width, height)

  with open(fname, 'w') as f:
    f.write('<?xml version="1.0"?>\n')
    f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    f.write('<svg width="{}in" height="{}in" viewBox="0 0 {} {}" xmlns="http://www.w3.org/2000/svg" version="1.1">\n'.format(
      float(width), float(height),
      float(width), float(height)
    ))
    f.write('<g transform="translate({},{}) scale(1,-1)" style="fill: none; stroke-linejoin: round;">\n'.format(
      float(-min_x),
      float(height + min_y)
    ))
    f.write(' <rect style="fill: none; stroke: #00f; stroke-width: 0.03;" x="{}" y="{}" width="{}" height="{}" />\n'.format(
      float(min_x), float(min_y),
      float(width), float(height)
    ))
    f.write(' <path style="fill: none; stroke-width: {}; stroke: #000;" d="{}" />\n'.format(
        float(Q(1,50) * mwh),
        tile_to_path_string(decomp_tile)
    ))
    f.write(' <path style="fill: none; stroke-width: {}; stroke: #f00;" d="{}" />\n'.format(
        float(Q(1,150) * mwh),
        tile_to_path_string(main_tile)
    ))
    vs = decomp_tile.vertices()
    for i, v1, v2 in zip(it.count(), vs, [*vs[1:], vs[0]]):
      anchor_pt = v1 + Q(1,2)*(v2-v1) + Q(1,10) * (v2-v1).rotate(5)
      f.write(' <g transform="translate({},{}) scale(1,-1)"><text style="font: {}px sans-serif; fill: #0cc;" x="0" y="0">{}</text></g>\n'.format(
        float(anchor_pt.x), float(anchor_pt.y),
        float(Q(1,30) * mwh),
        decomp_tile.matching_rules()[i]
      ))
    f.write('</g>\n')
    f.write('</svg>\n')


tiles = [
  (p.KiteTile(),   'to-A', 'kite-to-a'),
  (p.DartTile(),   'to-A', 'dart-to-a'),
  (p.ThickRhomb(), 'to-B', 'thick-to-b'),
  (p.ThinRhomb(),  'to-B', 'thin-to-b'),

  (p.A_K1(), 'half-deflation', 'hdef-ak1'),
  (p.A_K2(), 'half-deflation', 'hdef-ak2'),
  (p.A_D1(), 'half-deflation', 'hdef-ad1'),
  (p.A_D2(), 'half-deflation', 'hdef-ad2'),
  (p.B_L1(), 'half-deflation', 'hdef-bl1'),
  (p.B_L2(), 'half-deflation', 'hdef-bl2'),
  (p.B_S1(), 'half-deflation', 'hdef-bs1'),
  (p.B_S2(), 'half-deflation', 'hdef-bs2'),

  (p.A_K1(pg.translation(4,4) @ pg.rotation(4) @ pg.scaling(3)), 'half-deflation', 'ak1_mod-hdef'),

  (p.A_K1(), 'to-P2', 'ak1-to-p2'),
  (p.A_K2(), 'to-P2', 'ak2-to-p2'),
  (p.A_D1(), 'to-P2', 'ad1-to-p2'),
  (p.A_D2(), 'to-P2', 'ad2-to-p2'),
  (p.B_L1(), 'to-P3', 'bl1-to-p3'),
  (p.B_L2(), 'to-P3', 'bl2-to-p3'),
  (p.B_S1(), 'to-P3', 'bs1-to-p3'),
  (p.B_S2(), 'to-P3', 'bs2-to-p3'),

  (p.A_K1(), 'deflation', 'def-ak1'),
  (p.A_K2(), 'deflation', 'def-ak2'),
  (p.A_D1(), 'deflation', 'def-ad1'),
  (p.A_D2(), 'deflation', 'def-ad2'),
  (p.B_L1(), 'deflation', 'def-bl1'),
  (p.B_L2(), 'deflation', 'def-bl2'),
  (p.B_S1(), 'deflation', 'def-bs1'),
  (p.B_S2(), 'deflation', 'def-bs2'),
]

for t, decomp_id, stem in tiles:
  for i, d in zip(it.count(), t.decompose(decomp_id)):
    write_decomp_svg(t, d, 'dc/{}-{:02d}.svg'.format(stem, i))
