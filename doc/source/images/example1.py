from bdp import *

# New template called a_template derived from block with text_t attribute set
a_template = block(text_t='A Block')
# Set the color attribute
a_template.color = 'red'

# Render a_template
fig << a_template