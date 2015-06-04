from bdp import *
import inspect

def fill_group(group, fields, template):
    for name,text in fields:
        text = text.replace('_', '\_') 
        try:
            group[name] = template(text).align(group.at(-1).s())
        except IndexError:
            group[name] = template(text).align(group.n())
    
def uml_for_obj(obj, parent=object):
    
    # extract methods and attributes for diagram
    attrs = [(k, '+' + k) for k in sorted(obj.__dict__) if (k[0] != '_') and (not hasattr(parent, k))]
    methods = [(k, '+' + k[0] + '()')
                    for k in inspect.getmembers(obj, predicate=inspect.ismethod)
                        if (k[0][0] != '_') and (not hasattr(parent, k[0]))]
    
    # populate BDP blocks
    uml = block(r'\textbf{' + obj.__class__.__name__ + '}', alignment='tc', border=False, group='tight')
    field = block(size=(7,None), alignment='cw', border=False, text_margin=(0.2,0.1))

    uml['attrs'] = block(group='tight').align(uml.n())
    fill_group(uml['attrs'], attrs, field)
    
    uml['methods'] = block(group='tight').align(uml['attrs'].s())
    fill_group(uml['methods'], methods, field)

    return uml

block.nodesep = (4,2)

# generate UML components
element_uml = uml_for_obj(Element(), Node)
shape_uml = uml_for_obj(shape, Element())
block_uml = uml_for_obj(block, shape)
text_uml = uml_for_obj(text, Element())

# organize components in the diagram 
shape_uml.right(element_uml)
text_uml.below(shape_uml)
block_uml.right(text_uml).aligny(midy(text_uml.n(), shape_uml.n()))

# render the components
fig << element_uml << shape_uml << block_uml << text_uml

# generate and render the wiring
fig << path(text_uml.w(0.5), element_uml.e(0.6), style='-open triangle 45')
fig << path(shape_uml.w(0.5), element_uml.e(0.4), style='-open triangle 45')
fig << path(block_uml.w(0.5), shape_uml.e(0.4), style='-open triangle 45')
fig << path(block_uml['attrs']['text'].e(0.5), poff(1,0), text_uml.e(0.5), style='open diamond-', routedef='|-')
