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

def mid(p1, p2):
    return (p1 + p2)/2