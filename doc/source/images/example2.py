from bdp import *

t1 = block('T1')
t2 = block('T2').below(t1)
t3 = block('T3').left(t2)
t4 = block('T4').align(t1.e(0.2), prev().w(1))

fig << t1 << t2 << t3 << t4
