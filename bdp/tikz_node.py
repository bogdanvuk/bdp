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

class TikzMeta(object):

    _tikz_meta_options = []
    _tikz_len_measures = []
    _aliases = {}

    def _options(self, excluded=None):
        if not excluded:
            excluded = set()

        excluded |= set(self._tikz_meta_options)

        for s in self.__dict__:
            if s[0] != '_':
                if s not in excluded:
                    excluded.add(s)
                    yield s

        for s in self._def_settings:
            if s[0] != '_':
                if s not in excluded:
                    excluded.add(s)
                    yield s


    def _render_tikz_options(self, fig=None):
        options = []

        for s in self._options():
            try:
                options.append(getattr(self, "_render_tikz_" + s)(fig))
            except AttributeError:
                val = getattr(self, s)

                if s in self._aliases:
                    s = self._aliases[s]

                if val is True:
                    options.append(s.replace('_', ' '))
                elif val is not False:
                    if s in self._tikz_len_measures:
                        val = fig.to_units(val)
                        
                    options.append(s.replace('_', ' ') + '=' + str(val))

        return ','.join(options)


class TikzGroup(object):
    def _render_tikz(self, fig=None):
        tikz = ''
        for c in self:
            tikz += self[c]._render_tikz(fig)
            
        return tikz

class TikzNode(TikzMeta, TikzGroup):
    '''
    classdocs
    '''

    _tikz_meta_options = TikzMeta._tikz_meta_options +  ['p', 't']

    def _render_tikz_size(self, fig=None):
        if self.size:
            return "minimum width=" + fig.to_units(self.size[0]) + "," + "minimum height=" + fig.to_units(self.size[1])

    def _render_tikz_p(self, fig=None):
        pos = self.p + fig.origin + self.size/2
        return "{0}, {1}".format(fig.to_units(pos[0]), fig.to_units(pos[1]))

    def _render_tikz_t(self, fig=None):
        try:
            return self.t
        except AttributeError:
            return ''

    def _render_tikz(self, fig=None):
        try:
            pos = self._render_tikz_p(fig)
        except AttributeError:
            pos = ''

        if pos:
            pos = "at ({0})".format(pos)

        options = self._render_tikz_options(fig)

        if options:
            options = "[{0}]".format(options)

        text = self._render_tikz_t(fig)

        if text:
            text = "{{{0}}}".format(text)
        else:
            text = "{}"

        self_tikz = ' '.join(["\\node", pos, options, text, ";\n"])
        
        return self_tikz + TikzGroup._render_tikz(self, fig)


#     @property
#     def size(self):
#         return self.__getattr__('size')
# 
#     @size.setter
#     def size(self, value):
#         self.__dict__['size'] = p(value)
