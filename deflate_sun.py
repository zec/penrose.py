#!/usr/bin/env python3

import penrose
from tile_manager import TileManager
import tile_output as to
from pen_num import phi

def write_svg(tm, fname, include_arcs = False):
  with open(fname, 'w') as f:
    f.write('<?xml version="1.0"?>\n')
    f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    f.write('<svg width="70mm" height="70mm" viewBox="0 0 70 70" xmlns="http://www.w3.org/2000/svg" version="1.1">\n')
    f.write('<g transform="translate(35,35) scale(1,-1)">\n')
    if include_arcs:
      x = to.tiling_arcs_svg(tm, 3)
      f.write('  <path style="fill: none; stroke: #f99; stroke-width: 0.5; stroke-linecap: butt;" d="{}" />\n'.format(
        x['type1']
      ))
      f.write('  <path style="fill: none; stroke: #9f9; stroke-width: 0.5; stroke-linecap: butt;" d="{}" />\n'.format(
        x['type2']
      ))
    f.write('  <path style="fill: none; stroke: #99f; stroke-width: 0.25; stroke-linejoin: round; stroke-linecap: round;" d="{}" />\n'.format(
      to.tiling_to_svg_path(tm, 3)
    ))
    f.write('</g>\n')
    f.write('</svg>\n')

init_scale = phi * phi * phi * phi * phi * phi * phi
tm = TileManager()

for i in [-1, 3, 7, 11, 15]:
  tm.add_tile(penrose.KiteTile().scale(init_scale).rotate(i))

tm = tm.decompose('to-A')

niter = 8

for i in range(niter):
  write_svg(tm, 'sun/inter-{:02d}-A.svg'.format(i))
  write_svg(tm.decompose('to-P2'), 'sun/{:02d}-P2.svg'.format(i), True)
  tm = tm.decompose('half-deflation')
  write_svg(tm, 'sun/inter-{:02d}-B.svg'.format(i))
  write_svg(tm.decompose('to-P3'), 'sun/{:02d}-P3.svg'.format(i), True)
  if i == niter-1:
    break
  tm = tm.decompose('half-deflation')
