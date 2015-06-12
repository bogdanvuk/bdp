#  This file is part of bdp.
# 
#  Copyright (C) 2015 Bogdan Vukobratovic
#
#  bdp is free software: you can redistribute it and/or modify 
#  it under the terms of the GNU Lesser General Public License as 
#  published by the Free Software Foundation, either version 2.1 
#  of the License, or (at your option) any later version.
# 
#  bdp is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.
# 
#  You should have received a copy of the GNU Lesser General 
#  Public License along with bdp.  If not, see 
#  <http://www.gnu.org/licenses/>.

class Point(object):
    _eps = 1e-3
    
    def __init__(self, x, y=None):
        try:
            self.x = x[0]
            self.y = x[1]
        except TypeError:
            self.x = x
            self.y = y

    def __getitem__(self, key):
        if key == 0:
            return self.x
        else:
            return self.y

    def __setitem__(self, key, val):
        if key == 0:
            self.x = val
        else:
            self.y = val

    def copy(self):
        return Point(self.x, self.y)

    def __str__(self):
        return 'p({0},{1})'.format(self.x,self.y)

    __repr__ = __str__

    def __eq__(self, other):
        return (abs(self[0] - other[0]) < self._eps) and (abs(self[1] - other[1]) < self._eps)

    def __add__(self, other):
        return Point(self[0] + other[0], self[1] + other[1])

    def __radd__(self, other):
        return Point(self[0] + other[0], self[1] + other[1])

    def __div__(self, other):
        return Point(self[0] / other, self[1] / other)

    __truediv__ = __div__

    def __sub__(self, other):
        return Point(self[0] - other[0], self[1] - other[1])

    def __mul__(self, other):
        return Point(self[0] * other, self[1] * other)

    def __rmul__(self, other):
        return Point(self[0] * other, self[1] * other)

class Poff(Point):
    pass

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
