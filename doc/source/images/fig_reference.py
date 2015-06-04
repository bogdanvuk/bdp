from bdp import *

fig << block('Text1')
fig << block('Text2').right(fig['Te*'])
fig << block(r'Something \\ else').below(fig[-1])
fig << fig['S*'](text_color='blue').left(fig[0])