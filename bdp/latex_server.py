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