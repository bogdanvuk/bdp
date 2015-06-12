from bdp import *

def test_simple():

    fig << block('Text1')
    fig << block('Text2').right(fig['Te*'])
    fig << block(r'Something \\ else').below(fig[-1])
    fig << fig['S*'](text_color='blue').left(fig[0])
    
    assert fig['S*1'].p[0] == (fig['Text1'].p - fig['S*1'].size - (1, 0))[0] 