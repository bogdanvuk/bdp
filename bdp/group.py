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

from bdp.point import Point as p
import fnmatch

class Group(object):
    def __init__(self, *args, **kwargs):
        self.clear()

        self.append(*args, **kwargs)

    def clear(self):
        self._child = {}
        self._child_keys = []

    def add(self, obj):
        try:
            key = obj.t
        except AttributeError:
            try:
                key = obj.text.t
            except AttributeError:
                key = str(hash(obj))

        i = ''
        while ((key + i) in self._child_keys):
            if not i:
                i = '1'
            else:
                i = str(int(i) + 1)

        key += i

        self.__setitem__(key, obj)

        return self


    def __iadd__(self, obj):
        return self.add(obj)

    def _get_key(self, val):
        if isinstance(val, int):
            try:
                return self._child_keys[val], val
            except IndexError:
                raise
        elif isinstance(val, str):
            for i, t in enumerate(self._child_keys):
                if t == val:
                    return t, i
                else:
                    try:
                        if fnmatch.fnmatch(t, val + '*'):
                            return t, i
                    except AttributeError:
                        pass

            raise KeyError
        else:
            for i, t in enumerate(self._child_keys):
                if t == val:
                    return t,i

    def __delitem__(self, val):
        key, i = self._get_key(val)

        del self._child_keys[i]
        del self._child[key]

    def __getitem__(self, val):
        return self._child[self._get_key(val)[0]]

    def __setitem__(self, key, val):
        if key not in self._child:
            self._child_keys.append(key)

        self._child[key] = val

    def remove(self, val):
        self.__delitem__(val)

    def append(self, *args, **kwargs):
        for a in args:
            self += a

        for k,v in kwargs.items():
            self[k] = v

        return self

    def _bounding_box(self):
        cmin = p(float("inf"),float("inf"))
        cmax = p(float("-inf"),float("-inf"))

        if self._child:
            for k,v in self._child.items():
                if hasattr(v, '_bounding_box'):
                    bb = v._bounding_box()

                    for i in range(2):
                        if bb[0][i] < cmin[i]:
                            cmin[i] = bb[0][i]

                        if bb[1][i] > cmax[i]:
                            cmax[i] = bb[1][i]
        else:
            cmin = self.p
            cmax = self.p + self.size

        if hasattr(self, 'group_margin'):
            cmin -= self.group_margin[0]
            cmax += self.group_margin[1]

        return (cmin, cmax)

    def __iter__(self):
        for k in self._child_keys:
            yield k

    def __len__(self):
        return len(self._child_keys)
