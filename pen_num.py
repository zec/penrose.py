'''The number field Q[sqrt(2*(5+sqrt(5)))] -
a useful field to work in when handling Penrose tiles'''

from fractions import Fraction as Q
from math import sqrt, floor, ceil

def _fraction_as_string(q):
  if q.denominator == 1:
    return str(q.numerator)
  return '{}/{}'.format(q.numerator, q.denominator)

# The minimal polynomial sqrt(2*(5+sqrt(5))) is a zero of
# is x^4 - 20*x^2 + 80. As such, we can use _init_powers_of_alpha (defined
# later) to get a list of powers of alpha=sqrt(2*(5+sqrt(5))) in terms of
# (1, alpha, alpha^2, alpha^3):

_powers_of_alpha = []

# We use some interval arithmetic for correct comparison operations.
class RatInterval:
  def __init__(self, low, high=None):
    if isinstance(low, RatInterval):
      self.low, self.high = low.low, low.high
    elif high is None:
      self.low = Q(low)
      self.high = self.low
    else:
      self.low, self.high = Q(low), Q(high)

    if self.low > self.high:
      raise ValueError

  def midpoint(self):
    return (self.low + self.high) / 2

  def width(self):
    return self.high - self.low

  def _do_addition(self, other):
    try:
      o = RatInterval(other)
    except:
      return NotImplemented
    return RatInterval(self.low + o.low, self.high + o.high)

  def __add__(self, other):
    return self._do_addition(other)

  def __radd__(self, other):
    return self._do_addition(other)

  def __neg__(self):
    return RatInterval(-self.high, -self.low)

  def __sub__(self, other):
    return self._do_addition(-other)

  def __rsub__(self, other):
    return (-self)._do_addition(other)

  def _do_multiplication(self, other):
    try:
      o = RatInterval(other)
    except:
      return NotImplemented
    a = self.low  * o.low
    b = self.low  * o.high
    c = self.high * o.low
    d = self.high * o.high
    x = [a, b, c, d]
    return RatInterval(min(x), max(x))

  def __mul__(self, other):
    return self._do_multiplication(other)

  def __rmul__(self, other):
    return self._do_multiplication(other)

# For comparisons between two unequal Number objects,
# we use interval arithmetic to figure out which is greater...
# but for that, we need a possibly-narrow interval for alpha=sqrt(2*(5+sqrt(5))).
#
# Some facts: as mentioned, alpha is a zero of the polynomial
# f(x) = x^4 - 20*x^2 + 80. Alpha is in the interval [7/2, 4], on which f is
# monotonic increasing. Alpha is not a rational number. This allows
# for a very simple binary search to work. We implement it as follows:

def _generating_poly(x):
  return ((x * x - 20) * x * x) + 80

def _intervals_for_alpha():
  interval = RatInterval(Q(7,2), Q(4))
  yield interval

  while True:
    mdpt = interval.midpoint()
    if _generating_poly(mdpt) > 0:
      interval = RatInterval(interval.low, mdpt)
    else:
      interval = RatInterval(mdpt, interval.high)
    yield interval

_display_powers_of_alpha = [
  '{}', '{}*\u03b1', '{}*\u03b1\u00b2', '{}*\u03b1\u00b3'
]

# Our generator, as a floating-point number:
_pre_alpha = 10.0 + 2.0 * sqrt(5.0)
_float_alpha = sqrt(_pre_alpha)
_float_powers_of_alpha = (
  1.0,
  _float_alpha,
  _pre_alpha,
  _float_alpha * _pre_alpha
)

class Number:
  '''An element of the number field Q[sqrt(2*(5+sqrt(5)))]'''
  def __init__(self, e0 = 0, e1 = 0, e2 = 0, e3 = 0):
    if isinstance(e0, Number):
      self._vec = e0._vec
    else:
      self._vec = (Q(e0), Q(e1), Q(e2), Q(e3))

  def __repr__(self):
    return 'Number({}, {}, {}, {})'.format(*(repr(q) for q in self._vec))

  def __str__(self):
    s = []
    for i in range(len(self._vec)):
      if self._vec[i] != 0:
        s.append(_display_powers_of_alpha[i].format(_fraction_as_string(self._vec[i])))
    if len(s) == 0: # handle the case of zero
      s.append('0')
    return '<Number {}>'.format(' + '.join(s))

  def __neg__(self):
    return Number(*(-q for q in self._vec))

  def _do_addition(self, other):
    try:
      o = Number(other)
    except:
      return NotImplemented
    v1 = self._vec
    v2 = o._vec
    return Number(*( self._vec[i] + o._vec[i] for i in range(len(self._vec)) ))

  def __add__(self, other):
    return self._do_addition(other)

  def __radd__(self, other):
    return self._do_addition(other)

  def __sub__(self, other):
    return self + (-other)

  def __rsub__(self, other):
    return (-self) + other

  def _do_multiplication(self, other):
    if isinstance(other, int) or isinstance(other, Q):
      return Number(*(other * q for q in self._vec))
    # So, now that we've handled the simple case of multiplying
    # a Number by a rational number, we can use
    # that to handle the trickier case of two Numbers:
    elif isinstance(other, Number):
      s = self._vec
      o = other._vec
      coeffs = [
        s[0]*o[0],
        s[1]*o[0] + s[0]*o[1],
        s[2]*o[0] + s[1]*o[1] + s[0]*o[2],
        s[3]*o[0] + s[2]*o[1] + s[1]*o[2] + s[0]*o[3],
                    s[3]*o[1] + s[2]*o[2] + s[1]*o[3],
                                s[3]*o[2] + s[2]*o[3],
                                            s[3]*o[3]
      ]

      prod = Number(0)
      for i in range(len(coeffs)):
        prod += coeffs[i] * _powers_of_alpha[i]
      return prod
    else:
      return NotImplemented

  def __mul__(self, other):
    return self._do_multiplication(other)

  def __rmul__(self, other):
    return self._do_multiplication(other)

  # There is a multiplicative inverse, but we don't need it,
  # which is just as well - it's a little gnarly, and while
  # there would be ways to automate the process, they come
  # close to requiring a linear algebra package and implementing
  # most of a class for *general* number fields.

  # In a couple of places, we need to know how a Number compares
  # to some other number. We do that by using interval arithmetic,
  # using ever-more-accurate intervals bounding the generator alpha
  # to get ever-more-accurate intervals bounding self.
  def interval_sequence(self):
    '''Returns an interator yielding RatIntervals bounding self'''
    v = self._vec
    for alpha in _intervals_for_alpha():
      yield ((v[3] * alpha + v[2]) * alpha + v[1]) * alpha + v[0] # Horner's rule

  # OK, now we implement comparison functions. First off, is a
  # number less than, equal to, or greater than zero?
  def sgn(self):
    if all(q == 0 for q in self._vec): # exactly zero
      return 0
    # We use successively better intervals around alpha
    # to see whether our (now known to be non-zero) Number
    # is positive or not
    v = self._vec
    for approx in self.interval_sequence():
      if approx.low > 0: # *definitely* positive
        return 1
      if approx.high < 0: # *definitely* negative
        return -1
      # If we get here, we don't know whether self is positive
      # or negative yet. We start another iteration,
      # using a tighter bound on self.

  def __lt__(self, other):
    return (self - other).sgn() < 0

  def __le__(self, other):
    return (self - other).sgn() <= 0

  def __eq__(self, other):
    return (self - other).sgn() == 0

  def __ne__(self, other):
    return (self - other).sgn() != 0

  def __ge__(self, other):
    return (self - other).sgn() >= 0

  def __gt__(self, other):
    return (self - other).sgn() > 0

  # Returns false for 0, true for all other instantiable numbers
  def __bool__(self):
    return not all([q == 0 for q in self._vec])

  def __float__(self):
    return sum(float(self._vec[i]) * _float_powers_of_alpha[i] for i in range(4))

  def is_rational(self):
    # A Number is rational if and only if all of the {alpha, alpha^2, alpha3}
    # terms are zero:
    return all(q == 0 for q in self._vec[1:])

  def _do_floor(self):
    if self.is_rational():
      # when self is rational, we delegate:
      return floor(self._vec[0])
    else:
      # self is not rational (and in particular, not an integer):
      # bound it between two integers using successively tighter
      # intervals bounding it (the non-integrality ensures we'll exit the loop):
      v = self._vec
      for approx in self.interval_sequence():
        floor_low, floor_high = floor(approx.low), floor(approx.high)
        if floor_low == floor_high:
          return floor_low

  def __floor__(self):
    return self._do_floor()

  def __ceil__(self):
    if self.is_rational():
      return ceil(self._vec[0])
    else:
      # not rational, and in particular not an integer, so:
      return self._do_floor() + 1

  # int(x) is usually truncate-to-zero, and we do likewise
  def __int__(self):
    flr = self._do_floor()
    v = self._vec

    # if self is non-integer and negative:
    if ((v[0].denominator != 1) or not self.is_rational()) and self < 0:
      return flr + 1
    else:
      return flr

# The generator of the number field
alpha = Number(0, 1, 0, 0)

# The number one
one = Number(1, 0, 0, 0)

# The square root of five
sqrt5 = Number(-5, 0, Q(1,2), 0)

# The golden ratio
phi = (sqrt5 + 1) * Q(1,2)

# The inverse of the golden ratio, which conveniently is just phi-1
inv_phi = phi - one

def _init_powers_of_alpha():
  _alpha4 = (-80, 0, 20, 0) # alpha^4, expressed in terms of lesser powers of alpha
  _current_power = (1, 0, 0, 0) # start with alpha^0

  for n in range(7):
    _powers_of_alpha.append(Number(*_current_power))
    # Now, muliply by alpha:
    _shift_by_alpha = (0, _current_power[0], _current_power[1], _current_power[2])
    _current_power = tuple(_shift_by_alpha[i] + _current_power[3] * _alpha4[i] for i in range(4))

_init_powers_of_alpha()
