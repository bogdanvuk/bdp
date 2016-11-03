from bdp.latex_server import latex_server
from hypothesis import given, settings, strategies as st
import pytest

@pytest.mark.skip()
@given(st.floats(0, 1000), st.floats(0,1000), st.floats(0,10))
@settings(max_examples=5)
def test_node_size(width, height, line):
    epsilon = 1e-2
    s = latex_server.latex_query_node_size(r'\node at (0,0) [line width={:.2f}pt, minimum width={:.2f}pt,minimum height={:.2f}pt,draw,rectangle] {{}} ;'.format(line, width, height))

    assert abs(s[0] - (width + line)) < epsilon
    assert abs(s[1] - (height + line)) < epsilon
    # s = latex_server.latex_query_node_size(r'\draw (0,0) -- (4,0) -- (4,4) -- (0,4) -- (0,0);')
    # print(s)


def test_text_size():
    s = latex_server.latex_query_node_size(r'\node at (0,0) [text width=100pt, text height=50pt] {This is a demonstration text for showing how line breaking works.} ;')
    print(s)

