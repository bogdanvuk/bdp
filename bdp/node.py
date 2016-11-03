from bdp.point import Point as pt
from bdp.prototype import CallablePrototype
from collections import OrderedDict
from bdp.tikz_writer import TikzSizable, TikzHierarchy, TikzNode

class Node(CallablePrototype):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._writer = TikzNode()
        self.pos = pt(0,0)
        self.size = pt(1,1)

class SizableNodeBase(CallablePrototype):
    def __init__(self, **kwargs):
        self.sizable = False
        self._writer = TikzSizable()
        self.pos = pt(0,0)
        self._pad = [pt(0,0), pt(0,0)]
        self._size = pt(0,0)
        self.floating = False
        super().__init__(**kwargs)

    @property
    def size(self):
        if self.sizable:
            self._size = self.content_size + self.pad[0] + self.pad[1]

        return self._size

    @size.setter
    def size(self, val):
        self._size = val

        if self.sizable:
            diff = self._size - self.content_size
            rel_diff = pt(0,0)
            for i in range(2):
                if self._pad[0][i] + self._pad[1][i]:
                    rel_diff[i] = diff[i]/(self._pad[0][i] + self._pad[1][i])

            for i in range(2):
                self._pad[i] = self._pad[i]*rel_diff

    @property
    def pad(self):
        return self._pad

    @pad.setter
    def pad(self, val):
        self._pad = val

        if self.sizable:
            self._size = self.content_size + self._pad[0] + self._pad[1]

class HierNode(SizableNodeBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._child = OrderedDict()
        self._writer = TikzHierarchy()
        self._margin = [pt(0,0), pt(0,0)]

    def _content_bound_box(self):
        cmin = pt(float("inf"),float("inf"))
        cmax = pt(float("-inf"),float("-inf"))

        if self._child:
            for c in self._child:
                bb_min = self._child[c].pos
                bb_max = self._child[c].pos + self._child[c].size

                for i in range(2):
                    if bb_min[i] < cmin[i]:
                        cmin[i] = bb_min[i]

                    if bb_max[i] > cmax[i]:
                        cmax[i] = bb_max[i]
        else:
            cmin = self.pos
            cmax = self.pos

        return [cmin + self._margin[0], cmax - self._margin[1]]

    @property
    def content_size(self):
        bb  = self._content_bound_box()
        return bb[1] - bb[0]

    def __getitem__(self, key):
        return self._child[key]

    def __setitem__(self, key, val):
        self._child[key] = val

    def __len__(self):
        return len(self._child)

    def __iter__(self):
        return self._child.__iter__()
