from bdp import *

fig << path((0,0), (5,0), style=('<', cap(width=0.8, length=0.8, open=True)))
fig << path((0,2), (5,2), style=('<', cap(type='Stealth', width=1.2, length=2)), line_width=0.5, color='blue')
fig << path((0,4), (4,6), (6,6), routedef='-|', style=('', cap(width=1, length=1)), line_width=0.5, double=True, border_width=0.2, color='red')