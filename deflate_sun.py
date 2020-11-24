#!/usr/bin/env python3

import penrose
from tile_manager import TileManager
import tile_output as to

def write_svg(tm, fname):
  with open(fname, 'w') as f:
    f.write('<?xml version="1.0"?>\n')
    f.write('<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">\n')
    f.write('<svg width="200mm" height="200mm" viewBox="0 0 2.5 2.5" xmlns="http://www.w3.org/2000/svg" version="1.1">\n')
    f.write('<g transform="translate(1.25,1.25) scale(1,-1)">\n')
    f.write('  <path style="fill: none; stroke: #99f; stroke-width: 0.005; stroke-linejoin: round; stroke-linecap: round;" d="{}" />\n'.format(
      to.tiling_to_svg_path(tm, 3)
    ))
    f.write('</g>\n')
    f.write('</svg>\n')

tm = TileManager()
for i in [-1, 3, 7, 11, 15]:
  tm.add_tile(penrose.KiteTile().rotate(i))

tm = tm.decompose('to-A')

for i in range(10):
  write_svg(tm, 'sun/inter-{:02d}-A.svg'.format(i))
  write_svg(tm.decompose('to-P2'), 'sun/{:02d}-P2.svg'.format(i))
  tm = tm.decompose('half-deflation')
  write_svg(tm, 'sun/inter-{:02d}-B.svg'.format(i))
  write_svg(tm.decompose('to-P3'), 'sun/{:02d}-P3.svg'.format(i))
  tm = tm.decompose('half-deflation')
