from bdp import *

def test_arraws_meta():
    fig << path((0,0), (5,0), style=('<', cap(width=0.8, length=0.8, open=True)))
    fig << path((0,2), (5,2), style=('<', cap(type='Stealth', width=1.2, length=2)), line_width=0.5, color='blue')
    fig << path((0,4), (4,6), (6,6), routedef='-|', style=('', cap(width=1, length=1)), line_width=0.5, double=True, border_width=0.2, color='red')
    
def test_simple():
    fig << path((0,0), (1,1), (2,2), route=['--', '-|'])
    fig << path(fig[-1][0] + p(3,0), poff(1,1), poff(1,1), routedef='|-', style='<->', color='red')