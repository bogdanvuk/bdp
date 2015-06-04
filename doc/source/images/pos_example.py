from bdp import *

t = block(size = p(10,10))

dot = shape(shape='circle', size = p(0.4, 0.4), color='red', fill='red')

fig << '\draw[step=' + fig.to_units(1) + ',gray!40,very thin]' + \
        "({0}, {1}) grid ({2}, {3})".format(fig.to_units(-2), fig.to_units(-1), fig.to_units(12), fig.to_units(15)) + ';'

fig << t

fig << dot.align(t.s(0.5), dot.c())
fig << text('s(0.5)').align(dot.s(1.0))

fig << dot.align(t.s(1.0), dot.c())
fig << text('s(1.0)').align(dot.s(1.0))

fig << dot.align(t.e(0.2), dot.c())
fig << text('e(0.2)').align(dot.s(1.0))

fig << dot.align(t.e(7), dot.c())
fig << text('e(7)').align(dot.s(1.0))

fig << dot.align(t.n(), dot.c())
fig << text('n()').align(dot.n(1.0), prev().s())

fig << dot.align(t.n(12, -1), dot.c())
fig << text('n(12, -1)').align(dot.n(1.0), prev().s())

fig << dot.align(t.w(0.5, 1), dot.c())
fig << text('w(0.5, 1)').align(dot.s(), prev().n(1.0))

fig << dot.align(t.w(1.5, -0.2), dot.c())
fig << text('w(1.5, -0.2)').align(dot.s(), prev().n(1.0))

fig << dot.align(t.c(0.1,0.1), dot.c())
fig << text('c(0.1,0.1)').align(dot.n(1.0), prev().s(0.5))