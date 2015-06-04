from bdp import *

fig << path((0,0), (1,1), (2,2), route=['--', '-|'])
fig << path(fig[-1][0] + p(3,0), poff(1,1), poff(1,1), routedef='|-', style='<->', color='red')