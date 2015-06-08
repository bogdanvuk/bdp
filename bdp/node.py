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

from string import Template
import copy
import math
import tempfile
import os
from cgitb import text
import subprocess
import pexpect
import sys

from bdp.point import Point as p, Poff
import fnmatch

test = r"""
\documentclass{article}
\usepackage{tikz}
\usetikzlibrary{arrows.meta}
\begin{document}

\begin{tikzpicture}
\draw[black,step=1cm,thin] (0,0) grid (6,6);
\draw[-Latex[red,length=5mm,width=2mm],semithick] (0,1) -- (6,1);
\draw[-{Latex[red,length=5mm,width=2mm,angle'=90]},semithick] (0,1) -- (5,1);
\draw[-{Latex[red,length=5mm,width=2mm,angle'=45,open]},semithick] (0,1) -- (4,1);
\draw[-{Latex[red,length=5mm,width=2mm, angle=60:10pt]},semithick] (0,1) -- (3,1);
\draw[-{Stealth[scale=1.3,angle'=45]},semithick] (0,2) -- (6,2);
\draw[-{Stealth[scale=1.3,angle'=90]},semithick] (0,2) -- (5,2);
\draw[-{Stealth[scale=1.3,angle'=45,open]},semithick] (0,2) -- (4,2);
\draw[-{Stealth[scale=1.3,inset=1pt, angle=90:10pt]},semithick] (0,2) -- (3,2);
\end{tikzpicture}
\end{document}
"""

class Figure(object):
    grid    = 10
    origin  = p(1000, 1000)
    package = set(['tikz'])
    tikz_library = set(['shapes', 'arrows', 'decorations.pathreplacing', 'decorations.markings'])
    options = 'yscale=-1, every node/.style={inner sep=0,outer sep=0, anchor=center}'
    tikz_prolog = ''
#     tikz_prolog = r"""
# % for double arrows a la chef
# % adapt line thickness and line width, if needed
# \tikzstyle{thickarr} = [thick, decoration={markings,mark=at position
#    1 with {\arrow[semithick]{open triangle 60}}},
#    double distance=1.4pt, shorten >= 5.5pt,
#    preaction = {decorate},
#    postaction = {draw,line width=1.4pt, white,shorten >= 4.5pt}]
# \tikzstyle{innerWhite} = [semithick, white,line width=1.4pt, shorten >= 4.5pt]
# """
#     tikz_prolog = r"""
#     \tikzset{
#   double arrow/.style args={#1 colored by #2 and #3}{
#     -stealth,line width=#1,#2, % first arrow
#     postaction={draw,-stealth,#3,line width=(#1)/3,
#                 shorten <=(#1)/3,shorten >=2*(#1)/3}, % second arrow
#   }
# }
# """
    
    tikz_epilog = ''
    
    template = Template(r"""
\documentclass{standalone}

$packages
$tikz_libraries 

\begin{document}
\pagestyle{empty}
$tikz_prolog
\begin{tikzpicture}[$options]
$tikz
\end{tikzpicture}
$tikz_epilog
\end{document}
""")
    
#     tikz_prolog = r"""
# \documentclass{standalone}
# 
# \usepackage{tikz}
# \usetikzlibrary{shapes,arrows,decorations.pathreplacing}
# 
# \begin{document}
# \pagestyle{empty}
# \begin{tikzpicture}[yscale=-1, every node/.style={inner sep=0,outer sep=0, anchor=center}]
# 
#     """
# 
#     tikz_epilog = r"""
# \end{tikzpicture}
# 
# \end{document}
#     """
    
    def to_units(self,num):
        return "{0:.2f}{1}".format(num*self.grid, "pt")
    
    def from_units(self, s):
        s = s.replace('pt', '')
        return float(s) / self.grid
    
    def __init__(self):
        self._tikz = ''
        self._preamble = ''
        self._tmpl = []
    
    def _render_recursive(self, val):
        self._render_val(val)
        
        try:
            for k in val:
                self._render_recursive(val[k])
                
        except TypeError:
            pass
                
    def _render_val(self, val):
        if hasattr(val, '_render_tikz'):
            self._tikz += val._render_tikz(self) + '\n'
            self._tmpl.append(val)
        else:
            self._tikz += str(val)  + '\n'
    
    def __lshift__(self, val):
        self._render_recursive(val)
        return self
            
    def __getitem__(self, val):
        if isinstance(val, int):
            return self._tmpl[val]
        elif isinstance(val, str):
            match = ''
            for t in self._tmpl:
                try:
                    if fnmatch.fnmatch(t.t, val):
                        return t
                except AttributeError:
                    try:
                        if fnmatch.fnmatch(t.text.t, val):
                            return t
                    except AttributeError:
                        pass
                
            raise KeyError
        else:
            raise KeyError
                    
            
    def __str__(self):
        
#         return test
        
        packages = ''
        for p in self.package:
            packages += r'\usepackage{' + p + '}\n'

        tikz_libraries = ''
        for l in self.tikz_library:
            tikz_libraries += r'\usetikzlibrary{' + l + '}\n'
        
        return self.template.substitute(
                                        packages = packages,
                                        tikz_libraries = tikz_libraries,
                                        tikz_prolog = self.tikz_prolog,
                                        options = self.options,
                                        tikz = self._tikz,
                                        tikz_epilog = self.tikz_epilog
                                        )
#         return self.tikz_prolog + self._tikz.replace('\n', '\n    ') + self.tikz_epilog

obj_list = []
# tmpl_list = [None]
tmpl_cur = [None]

# def prev(i=0):
#     i = -(i+1)
#     return tmpl_list[i]

def prev(*args, **kwargs):
    if not args and not kwargs:
        return tmpl_cur[0]
    else:
        return tmpl_cur[0](*args, **kwargs)


class LatexServer(object):
    latex_preamble = r"""\documentclass{standalone}
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
"""
    
    def expect(self, tin, tout):
        self.proc.send(tin)
        buffer = []
        while (1):
            try:
                line = self.proc.readline()
            except pexpect.TIMEOUT:
                print(''.join(buffer))
                raise
            
            buffer += [line]
#             print(line)
            if line.startswith(tout):
                return line
    
    def __init__(self):
#         print('Init!')
        self.proc = pexpect.spawnu('pdflatex -draftmode -output-directory=' + tempfile.gettempdir(), timeout=0.5)
#         self.proc.expect('enabled.')
#         print(self.proc.before)
        self.proc.send(self.latex_preamble)


latex_server = LatexServer()

class TemplatedObjects(object):
    _def_settings = {}
    _template = None

    def __getattr__(self, attr, *args, **kwargs):
        try:
            return self.__dict__[attr]
        except (KeyError, TypeError):
            try:
                #if it is not special methods that are required
                if attr[0] != '_':
                    tokens = attr.split('_')
                    obj = tokens[0]
                    child_attr = '_'.join(tokens[1:])
                    if child_attr:
                        return getattr(getattr(self, obj), child_attr)
                    else:
                        raise AttributeError
                else:
                    raise AttributeError
            except (KeyError, TypeError, AttributeError):
#                 raise AttributeError
                raise AttributeError("%r object has no attribute %r" %
                                        (self.__class__, attr))
#         try:
#             return self.__dict__[attr]
#         except (KeyError, TypeError):
#             try:
#                 if attr[0] != '_':
#                     return copy.deepcopy(getattr(self._template, attr))
#                 else:
#                     raise AttributeError
#             except AttributeError:
#                 try:
#                     #if it is not special methods that are required
#                     if attr[0] != '_':
#                         tokens = attr.split('_')
#                         obj = tokens[0]
#                         child_attr = '_'.join(tokens[1:])
#                         if child_attr:
#                             return getattr(getattr(self, obj), child_attr)
#                         else:
#                             raise AttributeError
#                     else:
#                         raise AttributeError
#                 except (KeyError, TypeError, AttributeError):
#                     try:
#                         self.__dict__[attr] = copy.deepcopy(self._def_settings[attr])
#                         return self.__dict__[attr]
#                     except KeyError:
#                         raise AttributeError("%r object has no attribute %r" %
#                                             (self.__class__, attr))
            
#             try:
#                 if attr[0] != '_':
#                     return copy.deepcopy(getattr(self._template, attr))
#                 else:
#                     raise AttributeError
#             except AttributeError:
#                 try:
#                     self.__dict__[attr] = copy.deepcopy(self._def_settings[attr])
#                     return self.__dict__[attr]
#                 except KeyError:
#                     #if it is not special methods that are required
#                     if attr[0] != '_':
#                         try:
#                             tokens = attr.split('_')
#                             obj = tokens[0]
#                             child_attr = '_'.join(tokens[1:])
#                             if child_attr:
#                                 return getattr(getattr(self, obj), child_attr)
#                             else:
#                                 raise AttributeError
#                         except (KeyError, TypeError, AttributeError):
#                             raise AttributeError("%r object has no attribute %r" %
#                                             (self.__class__, attr))
#                     else:
#                         raise AttributeError("%r object has no attribute %r" %
#                                             (self.__class__, attr))

    def __setattr__(self, attr, val):
        if attr[0] == '_':
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
        
#         if attr[0] == '_':
#             super().__setattr__(attr, val)
#         else:
#             try:
#                 a = getattr(self, attr, val)
#                 super().__setattr__(attr, val)
#             except AttributeError:
#                 try:
#                     tokens = attr.split('_')
#                     obj = tokens[0]
#                     obj_attr = '_'.join(tokens[1:])
#                     if obj_attr:
#                         return setattr(getattr(self, obj), obj_attr, val)
#                     else:
#                         raise AttributeError
#                 except (KeyError, TypeError, AttributeError):
#                     super().__setattr__(attr, val)
#                 
#         if attr in self.__class__.__dict__:
#             super().__setattr__(attr, val)
#         else:
#             try:
#                 tokens = attr.split('_')
#                 obj = tokens[0]
#                 obj_attr = '_'.join(tokens[1:])
#                 if obj_attr:
#                     return setattr(getattr(self, obj), obj_attr, val)
#                 else:
#                     raise AttributeError
#             except (KeyError, TypeError, AttributeError):
#                 super().__setattr__(attr, val)

    def __call__(self, *args, **kwargs):

        kwargs['template'] = self

        tmpl_cur[0] = self.__class__(*args, **kwargs)

#        tmpl_list[-1] = tmpl_cur

        return tmpl_cur[0]

    def __init__(self, template=None, **kwargs):

        for k,v in self._def_settings.items():
            setattr(self, k, copy.deepcopy(v))
        
        if template is not None:
            for k,v in template.__dict__.items():
                setattr(self, k, copy.deepcopy(v))
##             self.__dict__.update(copy.deepcopy(template.__dict__))
        self._template = template
        
        for k,v in kwargs.items():
            setattr(self, k, copy.deepcopy(v))

#         self.__dict__.update(copy.deepcopy(kwargs))

class TikzMeta(TemplatedObjects):

    _tikz_meta_options = []
    _tikz_len_measures = []
#     _tikz_options = []
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

#         if self._template:
#             yield from self._template._options(excluded)

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

#                 if s in self._tikz_options:
                if val is True:
                    options.append(s.replace('_', ' '))
                elif val is not False:
                    if s in self._tikz_len_measures:
                        val = fig.to_units(val)
                        
                    options.append(s.replace('_', ' ') + '=' + str(val))

        return ','.join(options)

class Instance(TikzMeta):
    _tikz_meta_options = TikzMeta._tikz_meta_options +  ['type']
    
    def _render_tikz(self, fig=None):
        options = self._render_tikz_options(fig)
        if options:
            options = "[{0}]".format(options)
            
        return self.type + options 

class Node(TikzMeta):
    '''
    classdocs
    '''

    _tikz_meta_options = TikzMeta._tikz_meta_options +  ['p', 't']

#     def _render_tikz_font(self, fig=None):
#         return "font=\\" + self.font

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

        return ' '.join(["\\node", pos, options, text, ";"])


    @property
    def size(self):
        return self.__getattr__('size')

    @size.setter
    def size(self, value):
        self.__dict__['size'] = p(value)

def pos_decode(major='x'):

    def axis_decode_wrap(func):
        def coord(self, p1=None, p2=None, grid=None):
            pos = p(None, None)
            
            if major == 'x':
                maj_ind = 0
                min_ind = 1
            else:
                maj_ind = 1
                min_ind = 0
            
            try:
                pos = p(p1[0], p1[1])
            except (TypeError, KeyError):
                pos[maj_ind] = p1

            try:
                pos[min_ind] = p2[0]
            except (TypeError, KeyError):
                pos[min_ind] = p2
            
            for i in range(2):
                if pos[i] is None:
                    pos[i] = 0
                
            if grid is None:
                grid = self.grid
            else:
                grid_int = p(None, None)
                
                try:
                    grid_int = p(grid[0], grid[1])
                except (TypeError, KeyError):
                    grid_int[maj_ind] = grid

                for i in range(2):
                    if grid_int[i] is None:
                        grid_int[i] = self.grid[i]
                    
                grid = grid_int
            
            for i in range(2):
                if isinstance( pos[i], int ):
                    pos[i] *= grid[i]
                else:
                    pos[i] *= self.size[i]
            
            return func(self, pos)
        
        return coord
    
    return axis_decode_wrap

def axis_decode(axis='x'):

    def axis_decode_wrap(func):
        def coord(self, p1=None, grid=None):
            if axis == 'x':
                ax_ind = 0
            else:
                ax_ind = 1
            
            try:
                pos = p1[ax_ind]
            except TypeError:
                pos = p1
    
            if pos is None:
                pos = 0
                
            if grid is None:
                grid = self.grid
            else:
                grid_int = p(None, None)
                
                try:
                    grid_int = p(grid[0], grid[1])
                except (TypeError, KeyError):
                    grid_int[ax_ind] = grid

                for i in range(2):
                    if grid_int[i] is None:
                        grid_int[i] = self.grid[i]
                    
                grid = grid_int
            
            return func(self, pos, grid)
        
        return coord
    
    return axis_decode_wrap

class Element(Node):

    _def_settings = Node._def_settings.copy()
    _def_settings.update({
                            'p'      :  p(0,0),
                            'size'   :  p(None, None),
                            'grid'   :  p(1,1),
                        })
    
    _tikz_meta_options = Node._tikz_meta_options +  ['grid']

#     _tikz_options = Node._tikz_options + ['draw']

    def __init__(self, size=None, **kwargs):
        super().__init__(**kwargs)

        if size is not None:
            self.size = size

    def _render_tikz_size(self, fig):
        if self.size:
            return "minimum width=" + fig.to_units(self.size[0]) + "," + "minimum height=" + fig.to_units(self.size[1])

    def align(self, other, own=None):
        if own is None:
            own = self.p

        self.p = p(other) - (p(own) - self.p)

        return self

    def alignx(self, other, own=None):

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


    def aligny(self, other, own=None):
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

    @pos_decode()
    def c(self, pos):
        return self.p + self.size/2 + pos

    @pos_decode()
    def n(self, pos):
        return self.p + pos
    
    @axis_decode()
    def nx(self, pos, grid):
        return self.n(pos, 0, grid)[0]
    
    @pos_decode('y')
    def e(self, pos):
        return self.p + pos + (self.size[0], 0)

    @axis_decode('y')
    def ey(self, pos, grid):
        return self.e(pos, 0, grid)[1]

    @pos_decode()
    def s(self, pos):
        return self.p + pos + (0, self.size[1])
        
    @axis_decode()
    def sx(self, pos, grid):
        return self.s(pos, 0, grid)[0]

    @pos_decode('y')
    def w(self, pos=0):
        return self.p + pos
    
    @axis_decode('y')
    def wy(self, pos, grid):
        return self.w(pos, 0, grid)[1]

class Shape(Element):

#     meta_options = Element.meta_options + ['nodesep', 'conn_sep', 'border', 'anchor']

    _def_settings = Element._def_settings.copy()
    _def_settings.update({
            'border'        :  True,
            'nodesep'       : p(1,1),
            'group'         : None,
            'group_margin'  : p(0,0),
            'shape'         : 'rectangle'
            })

    _aliases = Element._aliases.copy()
    _aliases.update({
                    'border' : 'draw'
                    })
    
    _tikz_meta_options = Element._tikz_meta_options + ['nodesep', 'group', 'group_margin']
    
#     _tikz_options = Element._tikz_options + ['dotted', 'fill']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self._child = {}
        self._child_keys = []

    @property
    def size(self):
        if self.group == 'tight':
            if self._child:
                cmin = p(float("inf"),float("inf"))
                cmax = p(float("-inf"),float("-inf"))
    
                for k,v in self._child.items():
                    for i in range(2):
                        if v.n()[i] < cmin[i]:
                            cmin[i] = v.n()[i]
                        
                        if v.s(1.0)[i] > cmax[i]:
                            cmax[i] = v.s(1.0)[i]
        
                return cmax - cmin + 2*self.group_margin
            else:
                return p(0,0)
        else:
            return Node.size.__get__(self)

    
    @size.setter
    def size(self, value):
        Node.size.__set__(self, value)

    @property
    def p(self):
        if self.group == 'tight' and self._child:
            cmin = p(float("inf"),float("inf"))
            if self.group == 'tight':
                for k,v in self._child.items():
                    for i in range(2):
                        if v.n()[i] < cmin[i]:
                            cmin[i] = v.n()[i]
    
            return cmin - self.group_margin
        else:
            return self.__getattr__('p')   

    @p.setter
    def p(self, value):
        
        try:
            pcur = self.__getattr__('p')
        
            pdif = p(value) - pcur
        
            for _,v in self._child.items():
                v.p += pdif
        except AttributeError:
            pass
        
        self.__dict__['p'] = p(value)

    def __getitem__(self, key):
        return self._child[key]
    
    def __setitem__(self, key, val):
        if key not in self._child:
            self._child_keys.append(key)
            
        self._child[key] = val
        
    def __iter__(self):
        for k in self._child_keys:
            yield k

    def _render_tikz_shape(self, fig=None):
        return self.shape

    def at(self, ind):
        return self._child[self._child_keys[ind]]

    def a(self, angle=0):
        x = self.size[0]/2*math.cos(angle/180 * math.pi)
        y = self.size[0]/2*math.sin(angle/180 * math.pi)
        pos = p(x,-y) + self.size/2 + self.p

        return pos

    def r(self, x=0, y=0):
        return p(self.n(x)[0], self.w(y)[1])

    def n(self, p1=None, p2=None, grid=None):
        pos = super().n(p1, p2, grid)

        if self.shape == 'circle':
            r = self.size[0]/2
            x = pos[0] - self.p[0]
            y = r - math.sqrt(abs(2*r*x - x*x)) + self.p[1]
            pos[1] = y

        return pos

    def e(self, p1=None, p2=None, grid=None):
        pos = super().e(p1, p2, grid)

        if self.shape == 'circle':
            r = self.size[0]/2
            y = pos[1] - self.p[1]
            x = self.size[0] - (r - math.sqrt(abs(2*r*y - y*y))) + self.p[0]
            pos[0] = x

        return pos

    def s(self, p1=None, p2=None, grid=None):
        pos = super().s(p1, p2, grid)

        if self.shape == 'circle':
            r = self.size[0]/2
            x = pos[0] - self.p[0]
            y = self.size[1] - (r - math.sqrt(abs(2*r*x - x*x))) + self.p[1]
            pos[1] = y

        return pos

    def w(self, p1=None, p2=None, grid=None):
        pos = super().w(p1, p2, grid)

        if self.shape == 'circle':
            r = self.size[0]/2
            y = pos[1] - self.p[1]
            x = r - math.sqrt(abs(2*r*y - y*y)) + self.p[0]
            pos[0] = x

        return pos


    def over(self, other=None, pos=1):
        if other is None:
            other = self
            
        self.p = other.p - (0, self.size[1] + pos*other.nodesep[1])
        return self

    def right(self, other=None, pos=1):
        if other is None:
            other = self
            
        self.p = other.p + (other.size[0] + pos*other.nodesep[0], 0)
        return self

    def left(self, other=None, pos=1):
        if other is None:
            other = self
            
        self.p = other.p - (self.size[0] + pos*other.nodesep[0], 0)
        return self

    def below(self, other=None, pos=1):
        if other is None:
            other = self
            
        self.p = other.p + (0, other.size[1] + pos*other.nodesep[1])
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
    _aliases = Element._aliases.copy()
    _aliases.update({
                    'alignment': 'align'
                    })

    _def_settings = Element._def_settings.copy()
    _def_settings.update({
                        'border'        :  False,
                        'margin'        :  p(0.3,0.3),
                        'alignment'     : "center",
                        })

    _tikz_meta_options = Element._tikz_meta_options.copy()

    _memo = {}
    _size_measure = False

    def __init__(self, t=None, size=None, **kwargs):
        super().__init__(size, **kwargs)
        if t is not None:
            self.t = t

    def _render_tikz_p(self, fig=None):
        if self._size_measure:
            raise AttributeError
        else:
            return super()._render_tikz_p(fig)

    def _render_tikz_margin(self, fig=None):
        if self._size_measure:
            raise AttributeError

        if self.margin[0] is not None:
            return "text width=" + fig.to_units(self.size[0] - 2*self.margin[0])

        if self.margin[1] is not None:
            return "text height=" + fig.to_units(self.size[1] - 2*self.margin[1])

    def _get_size_from_text(self, size):
        if self.t:
            bdp_console_header = '[BDP]'

            self._tikz_meta_options.extend(['size', 'margin'])
            self._size_measure = True
            text = self._render_tikz(fig)
            self._tikz_meta_options.remove('size')
            self._tikz_meta_options.remove('margin')
            self._size_measure = False

            latex = Template(r"""\begin{tikzpicture}[every node/.style={inner sep=0,outer sep=0, anchor=center}]
\pgfpositionnodelater{\PgfPosition}%
$node
\setlength{\mywidth}{\mymaxx}%
\addtolength{\mywidth}{-\myminx}%
\global\mywidth=\mywidth
\setlength{\myheight}{\mymaxy}%
\addtolength{\myheight}{-\myminy}%
\global\myheight=\myheight
\typeout{$bdp_console_header\the\mywidth,\the\myheight}
\end{tikzpicture}
""")
            tin = latex.substitute(node=text,bdp_console_header=bdp_console_header)

            line = latex_server.expect(tin, '*' + bdp_console_header)

            line = line.replace('*' + bdp_console_header, '')
            vals = line.split(',')

            for i in range(2):
                if size[i] is None:
#                                 size[0] = math.ceil(from_units(vals[0]) + (2*self.margin[0]))
                    size[i] = fig.from_units(vals[i]) + (2*self.margin[i])

                    if size[i] == 0:
                        size[i] = 1

            return size
        else:
            return p(0,0)

    @property
    def size(self):
        try:
            set_size = self.__getattr__('size')
        except AttributeError:
            set_size = p(None,None)

        if (set_size[0] is None) or (set_size[1] is None):
            # size = self._memo.get('_get_size_from_text', self._get_size_from_text, (), {'size':size}, etag=self.t)
            if self.t in self._memo:
                size = self._memo[self.t]
            else:
                size = self._get_size_from_text(set_size)
                self._memo[self.t] = size
                
            for i in range(2):
                if set_size[i] is None:
                    set_size[i] = size[i]

        return set_size

    @size.setter
    def size(self, value):
        try:
            Element.size.__set__(self, value)
        except AttributeError:
            self.__dict__['size'] = value

class Block(Shape):
#     meta_options = Shape.meta_options + ['margin', 'text_align']

    _def_settings = Shape._def_settings.copy()
    _def_settings.update({
                         'alignment': 'cc'
                         })

#     text_args = ['margin', 'font']

    _tikz_meta_options = Shape._tikz_meta_options + ['alignment', 'text']

    text = None

    @property
    def alignment(self):
        return self.__getattr__('alignment')

    @alignment.setter
    def alignment(self, val):
        if len(val) == 1:
#             self.settings['text_align'] = val + 'c'
            self.__dict__['alignment'] = val + 'c'
        else:
#             self.settings['text_align'] = val
            self.__dict__['alignment'] = val

    def _render_tikz(self, fig=None):
#         self.text.p = self.p

#         self.text.align(self.n(), own)

        try:
            align = self.alignment
        except AttributeError:
            align = ''
            
        if align:
            if align[0] == 'n':
                yallign_self = self.wy()
                yallign_text = self.text.wy()
            elif align[0] == 'c':    
                self.text.size[1] = self.size[1]
                yallign_self = self.wy()
                yallign_text = self.text.wy()
            if align[0] == 's':
                yallign_self = self.wy(1.0)
                yallign_text = self.text.wy(1.0)
            elif align[0] == 't':
                yallign_self = self.wy()
                yallign_text = self.text.wy(1.0)
            elif align[0] == 'b':
                yallign_self = self.wy(1.0)
                yallign_text = self.text.wy()

            if align[1] == 'e':
                xallign_self = self.nx(1.0)
                xallign_text = self.text.nx(1.0)
                self.text.alignment = 'right'
            if align[1] == 'w':
                xallign_self = self.nx()
                xallign_text = self.text.nx()
                self.text.alignment = 'left'  
            elif align[1] == 'c':    
                self.text.size[0] = self.size[0]
                xallign_self = self.nx(0.0)
                xallign_text = self.text.nx(0.0)
                self.text.alignment = 'center'
                
            self.text.alignx(xallign_self, xallign_text)
            self.text.aligny(yallign_self, yallign_text)

#         try:
#             if self.text_align:
#                 if self.text_align == 'ne':
#                     self.text.p = self.e(0.0)
#                     self.text.anchor = self.text.e(0.0)
#                     self.text.text_align = 'right'
#                 elif self.text_align == 'nw':
#                     self.text.p = self.w(0.0)
#                     self.text.anchor = self.text.w(0.0)
#                     self.text.text_align = 'left'
#                 elif self.text_align == 'se':
#                     self.text.p = self.e(1.0)
#                     self.text.anchor = self.text.e(1.0)
#                     self.text.text_align = 'right'
#                 elif self.text_align == 'sw':
#                     self.text.p = self.w(1.0)
#                     self.text.anchor = self.text.w(1.0)
#                     self.text.text_align = 'left'
#                 elif self.text_align == 'nc':
#                     self.text.p = self.n(0.0)
#                     self.text.size[0] = self.size[0]
#                     self.text.anchor = self.text.n(0.0)
#                     self.text.text_align = 'center'
#                 elif self.text_align == 'sc':
#                     self.text.p = self.s(0.0)
#                     self.text.size[0] = self.size[0]
#                     self.text.anchor = self.text.s(0.0)
#                     self.text.text_align = 'center'
#                 elif self.text_align == 'oc':
#                     self.text.align(self.n(0.5), self.text.s(0.5))
#                     self.text.text_align = 'center'
#                 elif self.text_align == 'bc':
#                     self.text.align(self.s(0.5), self.text.n(0.5))
#                     self.text.text_align = 'center'
#                 else:
#                     self.text.p = self.p
#                     self.text.size = self.size
#                     if self.text_align[1] == 'w':
#                         self.text.text_align = 'left'
#                     elif self.text_align[1] == 'e':
#                         self.text.text_align = 'right'
#                     else:
#                         self.text.text_align = 'center'
# 
# #                 if self.align[0] == 'n':
# #                     self.text.size = p(None, self.size[1])
# #                     self.text.p = self.w(0.0)
# #                 elif self.align[0] == 'c':
# #                     self.text.size = self.size
# #                 elif self.align[0] == 's':
# #                     self.text.size = p(None, None)
# #                     self.text.p = self.s(1.0)
# #
# #                 if len(self.align) > 1:
# #                     if self.align[1] == 'w':
# #                         self.text.anchor = self.text.s(0.0)
# #                         self.text.align = 'left'
# #                     elif self.align[1] == 'c':
# #                         self.text.align = 'center'
# #                     elif self.align[1] == 'e':
# #                         self.text.anchor = self.text.s(1.0)
# #                         self.text.align = 'right'
#         except AttributeError:
#             pass

        text_node = self.text._render_tikz(fig)
#         text = self.t
#         self.t = None #Remove text so it wouldn't be printed twice
        shape_node = super()._render_tikz(fig)
#         self.t = text
        return shape_node + '\n' + text_node

    @property
    def size(self):
#         size = self.__getattr__('size')
        size = super(self.__class__, self.__class__).size.__get__(self)
        if (size[0] is None) or (size[1] is None):
            if self.group == 'tight':
                text_size = p(0,0)
            else:
                text_size = self.text.size
            
            for i in range(2):
                if size[i] is None:
                    size[i] = text_size[i]

        return size
    
    @size.setter
    def size(self, value):
        super(self.__class__, self.__class__).size.__set__(self, value)

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

class ArrowCap(Instance):
    _def_settings = Instance._def_settings.copy()
    _def_settings.update({
                        'type'          :  'Latex',
                        })
    
    _tikz_len_measures = Instance._tikz_len_measures + ['length', 'width']
    
    _tikz_meta_options = Instance._tikz_meta_options + ['fill_color']
    
    def _render_tikz(self, fig=None):
        fig.tikz_library.add('arrows.meta')
        return super()._render_tikz(fig)
    
cap = ArrowCap()

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
    _def_settings = TikzMeta._def_settings.copy()
    _def_settings.update({
                         'routedef'     : '--',
                         'path'         : [(0.0, 0.0)],
                         'route'        : [],
                         'smooth'       : False,
                         'draw'         : True,
                         'double'       : False,
                         'border_width' : 0.1,
                         'fill_color'   : 'white'
                         })

    _tikz_len_measures = TikzMeta._tikz_len_measures + ['line_width']
    _tikz_meta_options = TikzMeta._tikz_meta_options + ['path',  'smooth', 'route', 
                                                        'routedef', 'double', 'border_width',
                                                        'fill_color']
#     _tikz_options = TikzMeta._tikz_options + ['thick', 'ultra_thick', 'shorten',
#                                             'double', 'line_width', 'dotted', 
#                                             'looseness', 'rounded_corners', 
#                                             'draw', 'decorate', 'decoration']

    def _render_tikz_path(self, fig=None):
        path_tikz = []
        
        for p,r in zip(self.path, self.route):

            pos = p + fig.origin
            path_str = "(" + fig.to_units(pos[0]) + "," + fig.to_units(pos[1]) + ")"

            path_tikz.append(path_str)
            if not self.smooth:
                path_tikz.append('--')
#                 path_tikz.append(r)

        if not self.smooth:
            return ' '.join(path_tikz[:-1])
        else:
            return ' '.join(path_tikz)

    def _render_tikz_shorten(self, fig=None):
        return 'shorten <=' + fig.to_units(self.shorten[0]) + ',shorten >=' + fig.to_units(self.shorten[1])

    def _render_tikz_style(self, fig=None):
        
        if isinstance(self.style, str):
            return self.style
        else:
            cap = []
            for i in range(2):
                try:
                    cap.append('{' + self.style[i]._render_tikz(fig) + '}')
                except AttributeError:
                    cap.append(str(self.style[i]))

            return '{0}-{1}'.format(cap[0], cap[1])

    def _render_tikz_run(self, fig=None):
        options = self._render_tikz_options(fig)

        if options:
            options = "[{0}]".format(options)

        path = self._render_tikz_path(fig)

        if not self.smooth:
            return ' '.join(["\\path ", options, path, ";\n"])
        else:
            return ' '.join(["\\draw ", options, 'plot [smooth]', 'coordinates {', path, "};\n"])

    def _render_tikz(self, fig=None):
        tex = self._render_tikz_run(fig)
        
        if self.double:
            self_cpy = copy.deepcopy(self)
            w = self_cpy.border_width

            if not hasattr(self, 'shorten'):
                self_cpy.shorten = p(0,0)
            
#             self.shorten = 1.5*p(w,w) + self.shorten
#             self.line_width -= w
            self_cpy.shorten = 0.5*p(w,w) + self_cpy.shorten
            self_cpy.line_width -= w
            self_cpy.color = self_cpy.fill_color
            
            if not isinstance(self_cpy.style, str):
                self_cpy.style = [copy.deepcopy(self_cpy.style[0]), copy.deepcopy(self_cpy.style[1])]
            
            for i in range(2):
                try:
                    self_cpy.style[i].length -= 2*w
                    self_cpy.style[i].width -= 2*w
                    
#                     self_cpy.style[i].length -= w
#                     self_cpy.style[i].width -= w
                    try:
                        self_cpy.style[i].color = self_cpy.style[i].fill_color
                    except AttributeError:
                        self_cpy.style[i].color = self_cpy.fill_color
                    self_cpy.shorten[i] += w
                except (AttributeError, TypeError):
#                     self.shorten[i] -= 1.5*w
                    pass

            tex += '\n' + self_cpy._render_tikz_run(fig)
            
        return tex
        
    def __getitem__(self, key):
        if isinstance(key, slice):
            return Segment(key, self)
        else:
            return self.path[key]

    def pos(self, pos=0):
        return Segment(slice(0, len(self.path)), self).pos(pos)

    def c(self):
        return self.pos(0.5)

    def __init__(self, *path, **kwargs):
        super().__init__(**kwargs)

#         if route is not None:
#             self.route = route

        self.path = list(path)

        if path:
            
#             path_route_list = [itertools.zip_longest(self.path, self.route, fillvalue=self.routedef)]

            for i in range(len(self.path)):
                if i >= len(self.route):
                    self.route.append(self.routedef)

            for i in range(1, len(self.path)):
                if isinstance(self.path[i], Poff):
                    self.path[i] = self.path[i-1] + self.path[i]
                    
            i = 0
            while i < len(self.path) - 1:
                pos = self.path[i]
                pos_next = self.path[i+1]
                    
                route = self.route[i]
                if route == '|-':
                    if (pos[1] != pos_next[1]) and (pos[0] != pos_next[0]):
                        self.path.insert(i+1, p(pos[0], pos_next[1]))
                        self.route[i] = '--'
                        self.route.insert(i+1, '--')
                        i+=1
                elif route == '-|':
                    if (pos[1] != pos_next[1]) and (pos[0] != pos_next[0]):
                        self.path.insert(i+1, p(pos_next[0], pos[1]))
                        self.route[i] = '--'
                        self.route.insert(i+1, '--')
                        i+=1
                i+=1


origin = p(0, 0)

fig = Figure()
shape = Shape()
text = Text()
block = Block()
path = Path()
