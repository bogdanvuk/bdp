from bdp import *

# New template called template1 derived from block
template1 = block(text_t='A Block')
template1.color = 'red'

# Render template1
fig << template1