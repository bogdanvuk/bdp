import pytest
from bdp import *
import os
 
def pytest_runtest_setup(item):
    fig.clear()
    print ("setting up", item)
    
def pytest_runtest_teardown(item, nextitem):
    outname = os.path.splitext(item.parent.name)[0] + "_" + item.name + ".pdf"
    render_fig(fig, outname)
