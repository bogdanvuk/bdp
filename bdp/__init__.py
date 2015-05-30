try:
    import pkg_resources
    try:
        version = pkg_resources.get_distribution('bdp').version
    except pkg_resources.ResolutionError:
        version = None
except ImportError:
    version = None
    
from bdp.node import *
