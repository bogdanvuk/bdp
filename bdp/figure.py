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

import fnmatch
from bdp.point import Point as p
from string import Template
import copy
from bdp.group import Group

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

class Figure(Group):
    grid    = 10
    origin  = p(0, 0)
    package = set(['tikz'])
    tikz_library = set(['shapes', 'arrows', 'decorations.pathreplacing', 'decorations.markings'])
    options = 'yscale=-1, every node/.style={inner sep=0,outer sep=0, anchor=center}'
    tikz_prolog = ''
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

    def __init__(self):
        Group.__init__(self)
        self.clear()
        
    def clear(self):
        self._tikz = ''
        self._preamble = ''
#         self._tmpl = []
        self._live_func = None
        self._live_args = []
        self._live_kwargs = {}
        Group.clear(self)
    
    def to_units(self,num):
        return "{0:.2f}{1}".format(num*self.grid, "pt")
    
    def from_units(self, s):
        s = s.replace('pt', '')
        return float(s) / self.grid
    
    def live_preview_setup(self, live_func, args = [], kwargs = {}):
        self._live_func = live_func
        self._live_args = args
        self._live_kwargs = kwargs
    
#     def add(self, val):
#         if hasattr(val, '_render_tikz'):
#             self._tikz += val._render_tikz(self)
#         else:
#             self._tikz += str(val)
#             
#         self._tmpl.append(copy.deepcopy(val))
#         
#         if self._live_func is not None:
#             self._live_func(str(self), *self._live_args, **self._live_kwargs)
    
    __iadd__ = None
    
    def __lshift__(self, val):
        self.add(val)
        
        return self
    
    def __setitem__(self, key, val):
        if key not in self._child:
            self._child_keys.append(key)
            
            if hasattr(val, '_render_tikz'):
                self._tikz += val._render_tikz(self)
            else:
                self._tikz += str(val)
                
#             self._tmpl.append(copy.deepcopy(val))
            
            if self._live_func is not None:
                self._live_func(str(self), *self._live_args, **self._live_kwargs)
            
            
        self._child[key] = copy.deepcopy(val)
            
#     def __getitem__(self, val):
#         if isinstance(val, int):
#             return self._tmpl[val]
#         elif isinstance(val, str):
#             for t in self._tmpl:
#                 try:
#                     if fnmatch.fnmatch(t.t, val):
#                         return t
#                 except AttributeError:
#                     try:
#                         if fnmatch.fnmatch(t.text.t, val):
#                             return t
#                     except AttributeError:
#                         pass
#                 
#             raise KeyError
#         else:
#             raise KeyError
#                     
            
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


fig = Figure()
