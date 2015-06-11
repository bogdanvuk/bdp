from bdp import *
from bdp.node import Element
from bdp.render import render_fig 

def test_element():
    e = Element(size=p(1,1))
    
    e1 = e(t="e")
    e2 = e()
    e3 = e(t="e")
    
    g1 = group().extend(e1, e2)
    g1 += e3
    
    g1['e'].left(g1[-1])
    g1['e1'].right(g1[-1])
    
    assert(e1.p == p(-2,0))
    assert(e3.p == p(2,0))
    
    g1.p = p(10,10)
    assert(e2.p == p(10,10))
    
    g1.group = 'tight'
    g1 += e(t="e")
    
    assert(g1.size == (13, 11))
    
    del g1['e1']
    
    assert(g1.size == (11, 11))
    
def test_block():
    fig = Figure()
    
    mul_block = block("x", size=p(2,2), shape='circle')
    add_block = block("+", size=p(2,2), shape='circle')
    
    add2 = group()
    add2 += add_block()
    add2 += add_block().below(add2[-1], 2)
    add2 += add_block().align(mid(add2[-1].n(), add2[-2].n())).right(pos=2)
    
    fig << add2
    
#     render_fig(fig, 'test_block.pdf', options={'c': True})
    render_fig(fig, 'test_block.pdf')
    
test_block()