class Point(object):
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
    return p1/d + p2/(1-d)

@axis_decode('x')
def midx(p1, p2,d):
    return mid(p1,p2,d)

@axis_decode('y')
def midy(p1, p2,d):
    return mid(p1,p2,d)
