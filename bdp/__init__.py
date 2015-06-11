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

try:
    import pkg_resources
    try:
        version = pkg_resources.get_distribution('bdp').version
    except pkg_resources.ResolutionError:
        version = None
except ImportError:
    version = None

from bdp.point import Point as p, Poff as poff, Poffy as poffy, Poffx as poffx, mid, midy, midx
from bdp.node import block, prev, path, shape, text, Element, cap, group
from bdp.figure import fig, Figure
from bdp.render import render_fig
