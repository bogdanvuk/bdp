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

import pexpect
import tempfile
from bdp.point import Point as pt
from string import Template
import copy

class TikzSyntaxError(Exception):
    pass

class LatexServer(object):
    latex_preamble = r"""\documentclass{standalone}
\usepackage{calc}
\usepackage{tikz}
\usepackage{makecell}
\usepackage{amsmath}

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

    tikz_query_size = Template(r"""\begin{tikzpicture}[every node/.style={inner sep=0,outer sep=0, anchor=center}]
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

    bdp_console_header = '[BDP]'

    def __init__(self):
        self._node_size_memo = {}
        self.proc = pexpect.spawnu('pdflatex -draftmode -output-directory=' + tempfile.gettempdir(), timeout=2)
        self.proc.send(self.latex_preamble)

    def expect(self, tin, tout):
        # print(tin)
        self.proc.send(tin)
        buffer = []
        while (1):
            try:
                line = self.proc.readline()
            except pexpect.TIMEOUT:
                print(''.join(buffer))
                raise TikzSyntaxError

            buffer += [line]
#             print(line)
            if line.startswith(tout):
                return line

    def get_node_size(self, node):
        if node:
            if node in self._node_size_memo:
                size = copy.copy(self._node_size_memo[node])
            else:
                size = self.latex_query_node_size(node)
                self._node_size_memo[node] = copy.copy(size)

            return size
        else:
            return pt(0,0)

    def latex_query_node_size(self, node):
        tin = self.tikz_query_size.substitute(node=node,bdp_console_header=self.bdp_console_header)
        # print(tin)

        line = self.expect(tin, '*' + self.bdp_console_header)
        line = line.replace('*' + self.bdp_console_header, '')
        vals = line.split(',')

        size = pt(0,0)
        for i, v in enumerate(vals):
            v = v.replace('pt', '')
            size[i] = float(v)

        return size

latex_server = LatexServer()
