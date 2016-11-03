# The MIT License
#
# Copyright (c) 2015-2016 Bogdan Vukobratovic
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import numbers

class Point:
    _eps = 1e-3

    def __init__(self, x, y=None):
        if y is not None:
            try:
                self._coord = list([x[0],y[1]])
            except TypeError:
                self._coord = list([x,y])
        else:
            try:
                self._coord = list(x)
            except TypeError:
                self._coord = list([x,None])

    def __getitem__(self, key):
        return self._coord[key]

    def __setitem__(self, key, val):
        self._coord[key] = val

    def __copy__(self):
        return Point(self[0], self[1])

    def __str__(self):
        return 'pt({0},{1})'.format(self[0],self[1])

    def __len__(self):
        return 2

    def __iter__(self):
        return self._coord.__iter__()

    __repr__ = __str__

    def __eq__(self, other):
        return (abs(self[0] - other[0]) < self._eps) and (abs(self[1] - other[1]) < self._eps)

    def __add__(self, other):
        return Point(self[0] + other[0], self[1] + other[1])

    def __radd__(self, other):
        return Point(self[0] + other[0], self[1] + other[1])

    def __div__(self, other):
        if isinstance(other, numbers.Number):
            return Point(self[0] / other, self[1] / other)
        else:
            return Point(self[0] / other[0], self[1] / other[1])

    __truediv__ = __div__

    def __sub__(self, other):
        return Point(self[0] - other[0], self[1] - other[1])

    def __mul__(self, other):
        if isinstance(other, numbers.Number):
            return Point(self[0] * other, self[1] * other)
        else:
            return Point(self[0] * other[0], self[1] * other[1])

    def __imul__(self, other):
        if isinstance(other, numbers.Number):
            self[0] *= other
            self[1] *= other
        else:
            self[0] *= other[0]
            self[1] *= other[1]

        return self

    def __rmul__(self, other):
        return Point(self[0] * other, self[1] * other)

class Prel(Point):

    def __init__(self, rel):
        self.rel = rel

    def pabs(self, origin):
        return origin

class Poff(Prel):
    def pabs(self, origin):
        return origin + self.rel

class Poffx(Poff):
    def __init__(self, val):
        try:
            val = val[0]
        except TypeError:
            pass

        Poff.__init__(self, (val, 0))

class Poffy(Poff):
    def __init__(self, val):
        try:
            val = val[1]
        except TypeError:
            pass

        Poff.__init__(self, (0, val))

class Prectx(Prel):
    def pabs(self, origin):
        return Point(self.rel[0], origin[1])

class Precty(Prel):
    def pabs(self, origin):
        return Point(origin[0], self.rel[1])


def axis_decode(axis='x'):

    def axis_decode_wrap(func):
        def coord(p1, p2, d=2):
            if axis == 'x':
                ax_ind = 0
            else:
                ax_ind = 1

            try:
                p1 = p1[ax_ind]
            except TypeError:
                pass

            try:
                p2 = p2[ax_ind]
            except TypeError:
                pass

            return func(p1, p2, d)

        return coord

    return axis_decode_wrap

def mid(p1, p2, d=2):
    return p1/d + p2*(1-1/d)

@axis_decode('x')
def midx(p1, p2,d):
    return mid(p1,p2,d)

@axis_decode('y')
def midy(p1, p2,d):
    return mid(p1,p2,d)
