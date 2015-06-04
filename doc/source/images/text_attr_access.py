from bdp import *

b1 = block('Text1', text_color='red')
b2 = block('Text2').right(b1)

b2.text_font = r'\Large'
b2.text.color = 'blue'

fig << b1 << b2