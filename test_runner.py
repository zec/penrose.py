#!/usr/bin/env python3

# Test runner script. Takes one optional argument: an integer verbosity level.

import pen_num_tests, pen_geom_tests

modules_to_test = [
  pen_num_tests,
  pen_geom_tests,
]

if __name__ == '__main__':
  import unittest
  import sys

  suite = unittest.TestSuite()
  loader = unittest.defaultTestLoader
  suite.addTests(loader.loadTestsFromModule(m) for m in modules_to_test)

  verbosity = 1
  if len(sys.argv) > 1:
    try:
      verbosity = max(1, int(sys.argv[1]))
    except ValueError:
      sys.stderr.write('Invalid verbosity level "{}"\n'.format(sys.argv[1]))
      sys.exit(2)

  runner = unittest.TextTestRunner(verbosity = verbosity)
  result = runner.run(suite)
  if not result.wasSuccessful():
    sys.exit(1)
