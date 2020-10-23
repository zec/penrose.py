'''The number field Q[sqrt(2(5+sqrt(5)))] -
a useful field to work in when handling Penrose tiles'''

from fractions import Fraction as Q

def _fraction_as_string(q):
  if q.denominator == 1:
    return str(q.numerator)
  return '{}/{}'.format(q.numerator, q.denominator)

class Number:
  '''An element of the number field Q[sqrt(2(5+sqrt(5)))]'''
  def __init__(self, e0 = 0, e1 = 0, e2 = 0, e3 = 0):
    if isinstance(e0, Number):
      self._vec = e0._vec
    else:
      self._vec = (Q(e0), Q(e1), Q(e2), Q(e3))

  def __repr__(self):
    return 'Number({}, {}, {}, {})'.format(*[repr(q) for q in self._vec])

  def __str__(self):
    return '<Number {} + {}*\u03b1 + {}*\u03b1\u00b2 + {}*\u03b1\u00b3>'.format(*[_fraction_as_string(q) for q in self._vec])

  def __neg__(self):
    return Number(*[-q for q in self._vec])

  def _do_addition(self, other):
    try:
      o = Number(other)
    except:
      return NotImplemented
    v1 = self._vec
    v2 = o._vec
    return Number(*[self._vec[i] + o._vec[i] for i in range(len(self._vec))])

  def __add__(self, other):
    return self._do_addition(other)

  def __radd__(self, other):
    return self._do_addition(other)

  def __sub__(self, other):
    return self + (-other)

  def __rsub__(self, other):
    return other + (-self)


# The generator of the number field
alpha = Number(0, 1, 0, 0)

# The number one
one = Number(1, 0, 0, 0)

# The square root of five
sqrt5 = Number(-5, 0, Q(1,2), 0)
