from bdp import *
from bdp.node import Element

def test_element():
    e = Element(size=p(1,1))
    
    e1 = e(t="e")
    e2 = e()
    e3 = e(t="e")
    
    g1 = group().append(e1, e2)
    g1 += e3
    
    g1['e'].left(g1[-1])
    print(e1.p)
    print(e2.p)
    
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
   
    add_block = block("+", size=p(2,2), shape='circle')
    arrow = path(shorten=(1.5,1.5), style='->')
    
    add2 = group()
    add2 += add_block()
    add2 += add_block().below(add2[-1], 2)
    add2 += add_block().align(mid(add2[-1].c(), add2[-2].c()), prev().c()).right(pos=2)

    for i in range(2):
        add2 += arrow(add2[i].c(), add2[2].c())
        add2 += arrow(add2[i].c(), poffx(-6), style='<-')
    
    fig << add2
    
    add2.below()
    fig << add2
    
    fig << add_block().align(mid(fig[-1]['+2'].c(), fig[-2]['+2'].c()), prev().c()).right(pos=2)
    
    arr = []
    for i in range(2,4):
        arr.append(arrow(fig[-i]['+2'].c(), fig[-1].c()))
    
    arr.append(arrow(fig[-1].c(), poffx(6)))
    
    for a in arr:
        fig << a
        