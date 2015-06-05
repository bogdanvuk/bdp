from bdp import *

b1 = block('Text1', text_color='red')
b2 = block(r'$\displaystyle\lim_{x\to\infty} (1 + \frac{1}{x})^x$').right(b1)

b2.text_font = r'\Large'
b2.text.color = 'blue'

fig << b1 << b2