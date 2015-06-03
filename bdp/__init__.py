try:
    import pkg_resources
    try:
        version = pkg_resources.get_distribution('bdp').version
    except pkg_resources.ResolutionError:
        version = None
except ImportError:
    version = None

from bdp.point import Point as p, Poff as poff, Poffy as poffy, Poffx as poffx, mid, midy, midx
from bdp.node import block, fig, prev, path, shape, text, Element, Node
