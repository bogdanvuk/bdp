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

class TikzBase:
    _tikz_meta_options = []

    def render(self, obj, fig):
        pass

    def _attribute_gen(self, obj):
        for a in dir(obj):
            if not a.startswith('_'):
                if a not in self._tikz_meta_options:
                    yield a

    def _render_options(self, obj, fig):
        opts = []
        for a in self._attribute_gen(obj):
            render_func = getattr(self, 'render_{}'.format(a), None)
            if render_func is None:
                tikz = self._render_default(obj, a, fig)
            else:
                tikz = render_func(obj, fig)

            if tikz:
                opts.append(tikz)

        return ','.join(opts)

    def _render_default(self, obj, a, fig):
        return "{}={}".format(a.replace('_', ' '), getattr(obj, a))


class TikzNode(TikzBase):
    _tikz_meta_options = TikzBase._tikz_meta_options + ['pos', 'text', 'sizable']

    def render(self, obj, fig):
        pos = self.render_pos(obj, fig)
        opts = self._render_options(obj,fig)
        text = self.render_text(obj, fig)

        if text:
            return r"\node at ({}) [{}] {{{}}};".format(pos, opts, text) + "\n"
        else:
            return r"\node at ({}) [{}];".format(pos, opts) + "\n"

    def render_size(self, obj, fig):
        return "minimum width={0}, minimum height={1}".format(*fig.to_units(obj.size))

    def render_pos(self, obj, fig):
        pos = obj.pos + obj.size/2
        assert pos[0] == pos[0] #Check if NaN was obtained

        ret = "{0}, {1}".format(*fig.to_units(pos))
        return ret

    def render_text(self, obj, fig):
        try:
            tex = ''
            math_block = False
            escape_count = 0
            for c in obj.text:
                if c == '$':
                    math_block = not math_block

                if c == '_':
                    if (escape_count % 2 == 0) and (not math_block):
                        tex += '\_'
                    else:
                        tex += '_'
                else:
                    tex += c

                if c == '\\':
                    escape_count += 1
                else:
                    escape_count = 0

            return tex
        except (AttributeError, TypeError) as e:
            return ''

class TikzQueryTextSize(TikzNode):
    _tikz_meta_options = TikzNode._tikz_meta_options + ['pos', 'text']

    def render_size(self, obj, fig):
        if not obj.sizable:
            return "text width={0}".format(fig.to_units(obj._size)[0])

    def render_pos(self, obj, fig):
        return "0,0"
