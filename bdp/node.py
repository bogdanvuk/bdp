from bdp.point import Point as pt
from bdp.prototype import CallablePrototype
from collections import OrderedDict

class Node(CallablePrototype):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pos = pt(0,0)
        self.size = pt(1,1)
        self._child = OrderedDict()

    def __getitem__(self, key):
        return self._child[key]

    def __setitem__(self, key, val):
        self._child[key] = val

    def __len__(self):
        return len(self._child)

    def __iter__(self):
        return self._child.__iter__()

