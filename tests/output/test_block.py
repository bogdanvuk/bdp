from bdp import *

def test_simple():
    a_template = block(text_t='A Block')
    a_template.color = 'red'

    fig << a_template
    
def test_spacing():
    t1 = block('T1')
    t2 = block('T2').below(t1)
    t3 = block('T3').left(t2)
    t4 = block('T4').align(t1.e(0.2), prev().w(1))
    
    assert t1.p == (0,0)
    assert t2.p == (0, t1.size[1] + 1)
    assert t3.p == (t1.p[0] - t3.size[0] - 1, t1.size[1] + 1)
    assert t4.p == (t1.size[0],0.2*t1.size[1] - 1)
    
    fig << t1 << t2 << t3 << t4
    
def test_align():
    tblock = block(size = (7,5))
    
    vert = 'tncsb'
    hor = 'wce'
    
    for i,v in enumerate(vert):
        for j,h in enumerate(hor):
            print(v+h)
            fig << tblock(r"alignment \\ '"+v+h+"'", color='gray!70', alignment=v+h,p=(j*8, i*5.5))