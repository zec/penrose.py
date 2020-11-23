import re, math

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

