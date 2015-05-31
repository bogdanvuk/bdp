'''
Created on Mar 31, 2015

@author: Bogdan
'''
from string import Template
import copy
import math
from tempfile import NamedTemporaryFile
import os
from cgitb import text
import subprocess

from bdp.point import Point as p

class Figure(object):
    grid    = 10
    origin  = p(1000, 1000)
    
    def to_units(self,num):
        return "{0}{1}".format(num*self.grid, "pt")
    
    def from_units(self, s):
        s = s.replace('pt', '')
        return float(s) / self.grid
    
    def __init__(self):
        self._tikz = ''
        self._preamble = ''
    
    def __lshift__(self, val):
        if hasattr(val, '_render_tikz'):
            self._tikz += val._render_tikz(self) + '\n'
            tmpl_list.append(val)
        else:
            self._tikz += val  + '\n'

obj_list = []
tmpl_list = [None]
# tmpl_cur = None

def prev(i=0):
    i = -(i+1)
    return tmpl_list[i]


class TemplatedObjects(object):
    def_settings = {}
    children = []
    template = None

#     def __iter__(self):
#         return self
#
#     def __next__(self): # Python 3: def __next__(self)
#         if self.current > self.high:
#             raise StopIteration
#         else:
#             self.current += 1
#             return self.current - 1

    def __getattr__(self, attr, *args, **kwargs):
        try:
            return self.__dict__[attr]
        except (KeyError, TypeError):
            try:
                self.__dict__[attr] = copy.deepcopy(self.def_settings[attr])
                return self.__dict__[attr]
            except KeyError:
                #if it is not special methods that are required
                if attr[0] != '_':
                    try:
                        tokens = attr.split('_')
                        obj = tokens[0]
                        child_attr = '_'.join(tokens[1:])
                        if child_attr:
                            return getattr(getattr(self, obj), child_attr)
                        else:
                            raise AttributeError
                    except (KeyError, TypeError, AttributeError):
                        raise AttributeError("%r object has no attribute %r" %
                                            (self.__class__, attr))
                else:
                    raise AttributeError("%r object has no attribute %r" %
                                        (self.__class__, attr))

    def __setattr__(self, attr, val):
        if attr in self.__class__.__dict__:
            super().__setattr__(attr, val)
        else:
            try:
                tokens = attr.split('_')
                obj = tokens[0]
                obj_attr = '_'.join(tokens[1:])
                if obj_attr:
                    return setattr(getattr(self, obj), obj_attr, val)
                else:
                    raise AttributeError
            except (KeyError, TypeError, AttributeError):
                super().__setattr__(attr, val)

    def __call__(self, *args, **kwargs):

        kwargs['template'] = self

        tmpl_cur = self.__class__(*args, **kwargs)

        tmpl_list[-1] = tmpl_cur

        return tmpl_cur

    def copy(self):
        return self(template=self)

    def __init__(self, template=None, **kwargs):
        if template is not None:
            for k,v in template.__dict__.items():
                setattr(self, k, copy.deepcopy(v))
#             self.__dict__.update(copy.deepcopy(template.__dict__))

        for k,v in kwargs.items():
            setattr(self, k, copy.deepcopy(v))

#         self.__dict__.update(copy.deepcopy(kwargs))

class TikzMeta(TemplatedObjects):

    tikz_non_options = []
    tikz_options = []
    aliases = {}

    def options(self, excluded=None):
        if not excluded:
            excluded = set()

        excluded |= set(self.tikz_non_options)

#         for s in self.settings:
        for s in self.__dict__:
            if s not in excluded:
                excluded.add(s)
                yield s

        if self.template:
            yield from self.template.options(excluded)

        for s in self.def_settings:
            if s not in excluded:
                excluded.add(s)
                yield s


    def _render_tikz_options(self, fig=None):
        options = []

#         if self.border:
#             options.append('draw')

#         for s, val in self.settings.items():
#             if not s in self.meta_options:
        for s in self.options():
#             print(s)
            try:
                options.append(getattr(self, "_render_tikz_" + s)())
            except AttributeError:
                val = getattr(self, s)

                if s in self.aliases:
                    s = self.aliases[s]

                if s in self.tikz_options:
                    if val is True:
                        options.append(s.replace('_', ' '))
                    elif val is not False:
                        options.append(s.replace('_', ' ') + '=' + str(val))

        return ','.join(options)

class Node(TikzMeta):
    '''
    classdocs
    '''

    tikz_options = TikzMeta.tikz_options + ['align', 'anchor', 'font']
    tikz_non_options = TikzMeta.tikz_non_options +  ['p', 't', 'font_size', 'anchor']

#     def_settings = TikzMeta.def_settings.copy()
#     def_settings.update({
#                          'rel_anchor' : 'center'
#                          })

    aliases = TikzMeta.aliases.copy()
    aliases.update({
                    'rel_anchor'    : 'anchor'
                    })

    def _render_tikz_font(self, fig=None):
        return "font=\\" + self.font

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

        return ' '.join(["\\node", pos, options, text, ";\n"])


    @property
    def size(self):
        return self.__getattr__('size')

    @size.setter
    def size(self, value):
        self.__dict__['size'] = p(value)
#         super(self.__class__, self.__class__).size.__set__(self, p(value))
#         self.
#         super().__setattr__('size', p(value))

class Element(Node):
#     meta_options = ['anchor'] + Node.meta_options

    def_settings = Node.def_settings.copy()
    def_settings.update({
                            'p'      :  p(0,0),
                            'size'   :  p(None, None),
                            'anchor' :  p(0,0),
                        })

    tikz_options = Node.tikz_options + ['draw']

    def __init__(self, size=None, **kwargs):
        super().__init__(**kwargs)

        if size is not None:
            self.size = size

    def _render_tikz_size(self, fig):
        if self.size:
            return "minimum width=" + fig.to_units(self.size[0]) + "," + "minimum height=" + fig.to_units(self.size[1])

    def align(self, other, own=None):
#         self.anchor = own - other
#         return self

        if own is None:
            own = self.p

        self.p = p(other) - (p(own) - self.p)

        return self


    def align_x(self, other, own=None):
#         try:
#             self.anchor = p(own[0], self.anchor[1])
#         except TypeError:
#             self.anchor = p(own, self.anchor[1])

        try:
            other_x = other[0]
        except TypeError:
            other_x = other

        if own is None:
            own_x = self.p[0]
        else:
            try:
                own_x = own[0]
            except TypeError:
                own_x = own

        self.p = p(other_x - (own_x - self.p[0]), self.p[1])

        return self

#         try:
#             self.anchor = p((own - other)[0], self.p[1])
#         except TypeError:
#             self.anchor = p(own - other, self.p[1])
#         return self

    def align_y(self, other, own=None):
        try:
            other_y = other[1]
        except TypeError:
            other_y = other

        if own is None:
            own_y = self.p[1]
        else:
            try:
                own_y = own[1]
            except TypeError:
                own_y = own

        self.p = p(self.p[0], other_y - (own_y - self.p[1]))

        return self
#         try:
#             self.anchor = p(self.p[0], (own - other)[1])
#         except:
#             self.anchor = p(self.p[0], (own - other)[1])
#         return self

    def c(self, x=0, y=0):
        return p(self.n(x)[0] + self.size[0]/2, self.w(y)[1] + self.size[1]/2)

    def n(self, pos=0):
        return self.p + (pos * self.size[0], 0)

    def e(self, pos=0):
        return self.p + (self.size[0], pos * self.size[1])

    def s(self, pos=0):
        return self.p + (pos * self.size[0], self.size[1])

    def w(self, pos=0):
        return self.p + (0, pos * self.size[1])

class Shape(Element):

#     meta_options = Element.meta_options + ['node_sep', 'conn_sep', 'border', 'anchor']

    def_settings = Element.def_settings.copy()
    def_settings.update({
            'border' :  True,
            'node_sep' : p(1,1),
            'conn_sep' : 1,
            'shape' : 'rectangle'
            })

    aliases = Element.aliases.copy()
    aliases.update({
                    'border' : 'draw'
                    })

    tikz_options = Element.tikz_options + ['dotted', 'fill']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _render_tikz_shape(self):
        return self.shape

    def a(self, angle=0):
#         if self.shape == 'circle':
        x = self.size[0]/2*math.cos(angle/180 * math.pi)
        y = self.size[0]/2*math.sin(angle/180 * math.pi)
        pos = p(x,-y) + self.size/2 + self.p

        return pos
#         else:
#             return

    def r(self, x=0, y=0):
        return p(self.n(x)[0], self.w(y)[1])

    def n(self, pos=0):
        if isinstance( pos, int ):
            pos = self.p + (pos * self.conn_sep, 0)
        else:
            pos = super().n(pos)

        if self.shape == 'circle':
            r = self.size[0]/2
            x = pos[0] - self.p[0]
            y = r - math.sqrt(2*r*x - x*x) + self.p[1]
            pos[1] = y

        return pos

    def e(self, pos=0):
        if isinstance( pos, int ):
            pos = self.p + (self.size[0], pos * self.conn_sep)
        else:
            pos = super().e(pos)

        if self.shape == 'circle':
            r = self.size[0]/2
            y = pos[1] - self.p[1]
            x = self.size[0] - (r - math.sqrt(2*r*y - y*y)) + self.p[0]
            pos[0] = x

        return pos

    def s(self, pos=0):
        if isinstance( pos, int ):
            pos = self.p + (pos * self.conn_sep, self.size[1])
        else:
            pos = super().s(pos)

        if self.shape == 'circle':
            r = self.size[0]/2
            x = pos[0] - self.p[0]
            y = self.size[1] - (r - math.sqrt(2*r*x - x*x)) + self.p[1]
            pos[1] = y

        return pos

    def w(self, pos=0):
        if isinstance( pos, int ):
            pos = self.p + (0, pos * self.conn_sep)
        else:
            pos = super().w(pos)

        if self.shape == 'circle':
            r = self.size[0]/2
            y = pos[1] - self.p[1]
            x = r - math.sqrt(2*r*y - y*y) + self.p[0]
            pos[0] = x

        return pos

#     def r(self, pos):
#         return self.p + (self.size[0] + pos*self.node_sep[0], 0)

    def over(self, shape, pos=1):
#         return self.p - shape.anchor + (0, self.size[1] + pos*self.node_sep[1])
        self.p = shape.p - (0, self.size[1] + pos*shape.node_sep[1])
        return self

    def right(self, shape, pos=1):
#         return self.p - (pos*self.node_sep[0], 0)
        self.p = shape.p + (shape.size[0] + pos*shape.node_sep[0], 0)
        return self

    def left(self, shape, pos=1):
#         return self.p - (pos*self.node_sep[0], 0)
        self.p = shape.p - (self.size[0] + pos*shape.node_sep[0], 0)
        return self

    def below(self, shape, pos=1):
#         return self.p - shape.anchor + (0, self.size[1] + pos*self.node_sep[1])
        self.p = shape.p + (0, shape.size[1] + pos*shape.node_sep[1])
        return self

from os import kill
from signal import alarm, signal, SIGALRM, SIGKILL
from subprocess import PIPE, Popen

def run(args, cwd = None, shell = False, kill_tree = True, timeout = -1, env = None, universal_newlines=False ):
    '''
    Run a command with a timeout after which it will be forcibly
    killed.
    '''
    class Alarm(Exception):
        pass
    def alarm_handler(signum, frame):
        raise Alarm
    p = Popen(args, shell = shell, cwd = cwd, stdout = PIPE, stderr = PIPE, env = env, universal_newlines=universal_newlines)
    if timeout != -1:
        signal(SIGALRM, alarm_handler)
        alarm(timeout)
    try:
        stdout, stderr = p.communicate()
        if timeout != -1:
            alarm(0)
    except Alarm:
        pids = [p.pid]

        if kill_tree:
            pids.extend(get_process_children(p.pid))
        for pid in pids:
            # process might have died before getting to this line
            # so wrap to avoid OSError: no such process
            try:
                kill(pid, SIGKILL)
            except OSError:
                pass
        return -9, '', ''
#         return -9, stdout, stderr
    return p.returncode, stdout, stderr

def get_process_children(pid):
    p = Popen('ps --no-headers -o pid --ppid %d' % pid, shell = True,
              stdout = PIPE, stderr = PIPE)
    stdout, stderr = p.communicate()
    return [int(p) for p in stdout.split()]

class Text(Element):

#     meta_options = Element.meta_options + []
    aliases = Element.aliases.copy()
    aliases.update({
                    'text_align': 'align'
                    })

    def_settings = Element.def_settings.copy()
    def_settings.update({
                        'border'        :  False,
                        'margin'        :  p(0.3,0.3),
                        'text_align'    : "center",
                        })

    tikz_non_options = Element.tikz_non_options.copy()

    memo = {}
    size_measure = False

    def __init__(self, t=None, size=None, **kwargs):
        super().__init__(size, **kwargs)
        if t is not None:
            self.t = t

    def _render_tikz_p(self, fig=None):
        if self.size_measure:
            raise AttributeError
        else:
            return super()._render_tikz_p(fig)

    def _render_tikz_margin(self, fig=None):
        if self.size_measure:
            raise AttributeError

        if self.margin[0] is not None:
            return "text width=" + fig.to_units(self.size[0] - 2*self.margin[0])

        if self.margin[1] is not None:
            return "text height=" + fig.to_units(self.size[1] - 2*self.margin[1])

    def _get_size_from_text(self, size):
        if self.t:
            bdp_console_header = '[BDP]'

            self.tikz_non_options.extend(['size', 'margin'])
            self.size_measure = True
            text = self._render_tikz(fig)
            self.tikz_non_options.remove('size')
            self.tikz_non_options.remove('margin')
            self.size_measure = False

#             latex = Template(r"""\documentclass{article}
# \begin{document}
# \newlength\mywidth
# \newlength\myheight
# \settowidth{\mywidth}{$text}
# \settoheight{\myheight}{$text}
# \typeout{$bdp_console_header\the\mywidth,\the\myheight}
# \end{document}""")
            latex = Template(r"""\documentclass{article}
\usepackage{calc}
\usepackage{tikz}
\usepackage{makecell}

\newlength\mywidth
\newlength\myheight
\newlength\myminx
\newlength\mymaxx
\newlength\myminy
\newlength\mymaxy

\newcommand{\PgfPosition}{%
    \global\let\myminx=\pgfpositionnodelaterminx%
    \global\let\mymaxx=\pgfpositionnodelatermaxx%
    \global\let\myminy=\pgfpositionnodelaterminy%
    \global\let\mymaxy=\pgfpositionnodelatermaxy%
}%

\begin{document}
\begin{tikzpicture}[every node/.style={inner sep=0,outer sep=0, anchor=center}]
\pgfpositionnodelater{\PgfPosition}%
$node
\setlength{\mywidth}{\mymaxx}%
\addtolength{\mywidth}{-\myminx}%
\global\mywidth=\mywidth
\setlength{\myheight}{\mymaxy}%
\addtolength{\myheight}{-\myminy}%
\global\myheight=\myheight
\end{tikzpicture}

\typeout{$bdp_console_header\the\mywidth,\the\myheight}
\end{document}""")

            f = NamedTemporaryFile(delete=False)
            f.write(latex.substitute(node=text,bdp_console_header=bdp_console_header).encode())

            temp_dir = os.path.dirname(f.name)

            latex_cmd = 'latex ' + f.name + \
                        ' -draftmode -interaction=errorstopmode' + \
                        ' -output-directory=' + temp_dir

            f.close()

            try:
                origWD = os.getcwd() # remember our original working directory

                os.chdir(temp_dir)

#                 ret = subprocess.check_output(tex, shell=True, universal_newlines=True, timeout=1)
                ret_code,ret,ret_err = run(latex_cmd, shell=True, universal_newlines=True, timeout=1)

                for line in ret.split('\n'):
                    if line.startswith(bdp_console_header):
                        line = line.replace(bdp_console_header, '')
                        vals = line.split(',')

                        for i in range(2):
                            if size[i] is None:
#                                 size[0] = math.ceil(from_units(vals[0]) + (2*self.margin[0]))
                                size[i] = fig.from_units(vals[i]) + (2*self.margin[i])

                                if size[i] == 0:
                                    size[i] = 1

#                             if size[1] is None:
# #                                 size[1] = math.ceil(from_units(vals[1]) + (2*self.margin[1]))
#                                 size[1] = from_units(vals[1]) + (2*self.margin[1])
#
#                                 if size[1] == 0:
#                                     size[1] = 1

                        break

            except subprocess.CalledProcessError as e:
                print ("Ping stdout output:\n", e.output)
            finally:
                os.unlink(f.name)
#                 for f in glob (os.path.join(temp_dir, '*.aux')):
#                     os.unlink(f)
#                 for f in glob (os.path.join(temp_dir, '*.dvi')):
#                     os.unlink(f)
#                 for f in glob (os.path.join(temp_dir, '*.log')):
#                     os.unlink(f)

                os.chdir(origWD) # get back to our original working directory

            return size
        else:
            return p(1,1)

    @property
    def size(self):
        try:
            size = self.__getattr__('size')
        except AttributeError:
            size = p(None,None)

        if (size[0] is None) or (size[1] is None):
            # size = self.memo.get('_get_size_from_text', self._get_size_from_text, (), {'size':size}, etag=self.t)
            if self.t in self.memo:
                size = self.memo[self.t]
            else:
                size = self._get_size_from_text(size)
                self.memo[self.t] = size

        return size

    @size.setter
    def size(self, value):
        try:
            Element.size.__set__(self, value)
        except AttributeError:
            self.__dict__['size'] = value

class Block(Shape):
#     meta_options = Shape.meta_options + ['margin', 'text_align']

    def_settings = Shape.def_settings.copy()
    def_settings.update({
                         'text_align': 'cc'
                         })

#     text_args = ['margin', 'font']

    text = None

    @property
    def text_align(self):
        return self.__getattr__('text_align')

    @text_align.setter
    def text_align(self, val):
        if len(val) == 1:
#             self.settings['text_align'] = val + 'c'
            self.__dict__['text_align'] = val + 'c'
        else:
#             self.settings['text_align'] = val
            self.__dict__['text_align'] = val

    def _render_tikz(self, fig=None):
        self.text.p = self.p

        try:
            if self.text_align:
                if self.text_align == 'ne':
                    self.text.p = self.e(0.0)
                    self.text.anchor = self.text.e(0.0)
                    self.text.text_align = 'right'
                elif self.text_align == 'nw':
                    self.text.p = self.w(0.0)
                    self.text.anchor = self.text.w(0.0)
                    self.text.text_align = 'left'
                elif self.text_align == 'se':
                    self.text.p = self.e(1.0)
                    self.text.anchor = self.text.e(1.0)
                    self.text.text_align = 'right'
                elif self.text_align == 'sw':
                    self.text.p = self.w(1.0)
                    self.text.anchor = self.text.w(1.0)
                    self.text.text_align = 'left'
                elif self.text_align == 'nc':
                    self.text.p = self.n(0.0)
                    self.text.size[0] = self.size[0]
                    self.text.anchor = self.text.n(0.0)
                    self.text.text_align = 'center'
                elif self.text_align == 'sc':
                    self.text.p = self.s(0.0)
                    self.text.size[0] = self.size[0]
                    self.text.anchor = self.text.s(0.0)
                    self.text.text_align = 'center'
                elif self.text_align == 'oc':
                    self.text.align(self.n(0.5), self.text.s(0.5))
                    self.text.text_align = 'center'
                elif self.text_align == 'bc':
                    self.text.align(self.s(0.5), self.text.n(0.5))
                    self.text.text_align = 'center'
                else:
                    self.text.p = self.p
                    self.text.size = self.size
                    if self.text_align[1] == 'w':
                        self.text.text_align = 'left'
                    elif self.text_align[1] == 'e':
                        self.text.text_align = 'right'
                    else:
                        self.text.text_align = 'center'

#                 if self.align[0] == 'n':
#                     self.text.size = p(None, self.size[1])
#                     self.text.p = self.w(0.0)
#                 elif self.align[0] == 'c':
#                     self.text.size = self.size
#                 elif self.align[0] == 's':
#                     self.text.size = p(None, None)
#                     self.text.p = self.s(1.0)
#
#                 if len(self.align) > 1:
#                     if self.align[1] == 'w':
#                         self.text.anchor = self.text.s(0.0)
#                         self.text.align = 'left'
#                     elif self.align[1] == 'c':
#                         self.text.align = 'center'
#                     elif self.align[1] == 'e':
#                         self.text.anchor = self.text.s(1.0)
#                         self.text.align = 'right'
        except AttributeError:
            pass

        text_node = self.text._render_tikz(fig)
#         text = self.t
#         self.t = None #Remove text so it wouldn't be printed twice
        shape_node = super()._render_tikz(fig)
#         self.t = text
        return shape_node + '\n' + text_node

    def __init__(self, text_t=None, size=None, **kwargs):

        text_args_dict = {}

#         for a in self.text_args:
#             if a in kwargs:
#                 text_args_dict[a] = kwargs[a]
#                 kwargs.pop(a)

        self.text = Text()

        super().__init__(size, **kwargs)

        if text_t is not None:
#             text_args_dict['t'] = t
            self.text_t = text_t



        for k,v in text_args_dict.items():
            setattr(self.text, k, v)

class Segment(object):

    def _seglen(self, p1, p2):
        if p1[0] == p2[0]:
            return abs(p1[1] - p2[1])
        elif p1[1] == p2[1]:
            return abs(p1[0] - p2[0])
        else:
            return math.sqrt(math.pow(p1[0] - p2[0], 2) + math.pow(p1[1] - p2[1], 2))

    def __iter__(self):
        return iter(self.path)

    def len(self):
        tot_len = 0
        last = self.path[self.slice.start]
        for cur in self.path.path[self.slice.start+1: self.slice.stop+1]:
            tot_len += self._seglen(cur, last)
        return tot_len

    def pos(self, pos=0.0):
        pos_len = pos*self.len()

        cur_len = 0
        last = self.path[self.slice.start]
        for cur in self.path.path[self.slice.start+1: self.slice.stop+1]:
            last_len = cur_len
            cur_len += self._seglen(cur, last)

            if cur_len > pos_len:
                return p(last[0] + (cur[0] - last[0])*(pos_len - last_len)/(cur_len - last_len),
                         last[1] + (cur[1] - last[1])*(pos_len - last_len)/(cur_len - last_len))


    def __init__(self, slice, path):
        self.slice = slice
        self.path = path


class Path(TikzMeta):
    def_settings = TikzMeta.def_settings.copy()
    def_settings.update({
                         'def_routing'    : '--',
                         'path'         : [(0.0, 0.0)],
                         'routing'      : [],
                         'margin'       : [0, 0],
                         'smooth'       : False,
                         'draw'         : True
                         })

    tikz_non_options = TikzMeta.tikz_non_options + ['path',  'smooth']
    tikz_options = TikzMeta.tikz_options + ['thick', 'ultra_thick', 'shorten',
                                            'double', 'line_width', 'dotted', 
                                            'looseness', 'rounded_corners', 
                                            'draw', 'decorate', 'decoration']

    def _render_tikz_path(self, fig=None):
        path_tikz = []
        
        for p,r in zip(self.path, self.routing):

            pos = p + fig.origin
            path_str = "(" + fig.to_units(pos[0]) + "," + fig.to_units(pos[1]) + ")"

            path_tikz.append(path_str)
            if not self.smooth:
                path_tikz.append(r)

        if not self.smooth:
            return ' '.join(path_tikz[:-1])
        else:
            return ' '.join(path_tikz)

    def _render_tikz_shorten(self, fig=None):
        return 'shorten <=' + fig.to_units(self.shorten[0]) + ',shorten >=' + fig.to_units(self.shorten[1])

    def _render_tikz_style(self, fig=None):
        return self.style

    def _render_tikz(self, fig=None):

        options = self._render_tikz_options(fig)

        if options:
            options = "[{0}]".format(options)

        path = self._render_tikz_path(fig)

        if not self.smooth:
            return ' '.join(["\\path ", options, path, ";\n"])
        else:
            return ' '.join(["\\draw ", options, 'plot [smooth]', 'coordinates {', path, "};\n"])

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Segment(key, self)
        else:
            return self.path[key]

    def pos(self, pos=0):
        return Segment(slice(0, len(self.path)), self).pos(pos)

    def c(self):
        return self.pos(0.5)

    def __init__(self, path=None, routing=None, **kwargs):
        super().__init__(**kwargs)

        if routing is not None:
            self.routing = routing

        if path is not None:
            self.path = path
#             path_route_list = [itertools.zip_longest(self.path, self.routing, fillvalue=self.def_routing)]

            for i in range(len(self.path)):
                if i >= len(self.routing):
                    self.routing.append(self.def_routing)

            i = 0
            while i < len(self.path) - 1:
                pos = self.path[i]
                pos_next = self.path[i+1]
                route = self.routing[i]
                if route == '|-':
                    if (pos[1] != pos_next[1]) and (pos[0] != pos_next[0]):
                        self.path.insert(i+1, p(pos[0], pos_next[1]))
                        self.routing[i] = '--'
                        self.routing.insert(i+1, '--')
                        i+=1
                elif route == '-|':
                    if (pos[1] != pos_next[1]) and (pos[0] != pos_next[0]):
                        self.path.insert(i+1, p(pos_next[0], pos[1]))
                        self.routing[i] = '--'
                        self.routing.insert(i+1, '--')
                        i+=1
                i+=1


origin = p(0, 0)

fig = Figure()
shape = Shape()
text = Text()
block = Block()
path = Path()


