from bdp import *

block.size=(6,3)
block.nodesep=(3,3)

BDP = block(r"BDP", alignment='nw', group='tight', group_margin=p(1,1.5), dashed=True)
fig << block(r"Python \\ Description")
BDP['tikz'] = prev(r"TikZ \\ Renderer").right()
BDP['pdf'] = prev(r"PDF \\ Renderer").below()
BDP['png'] = prev(r"PNG \\ Renderer").below()
fig << prev(r"TeX Live", size=(6,9)).right(BDP['tikz'])
fig << block(r"pdftoppm \\ pnmtopng").below(fig['Te*'])

fig << BDP

fig << path(fig['Pyt*'].e(0.5), BDP['tikz'].w(0.5), style='->')
fig << path(fig['Tik*'].s(0.5), fig['PDF*'].n(0.5), style='->')
fig << text('TeX').align(fig[-1].pos(0.5), prev().w(0.5))

fig << path(fig['PDF*'].s(0.5), fig['PNG*'].n(0.5), style='->')
fig << text('PDF').align(fig[-1].pos(0.5), prev().w(0.5))

fig << path(fig['PNG*'].s(0.5), poffy(3), style='->')
fig << text('PNG').align(fig[-1].pos(0.9), prev().w(0.5))
        
fig << path(BDP['tikz'].e(0.5), poffx(3), style='<->')
fig << path(fig['PDF*'].e(0.5), poffx(3), style='<->')
fig << path(fig['PNG*'].e(0.5), poffx(3), style='<->')