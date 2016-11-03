from bdp.node import Node, HierNode
from bdp.text import Text
from bdp.point import Point as pt
from bdp.tikz_writer import TikzNode

class Figure:
    grid = pt(1,10)

    def to_units(self, p):
        ret = []
        for pc, gc in zip(p, self.grid):
            ret.append("{0:.2f}{1}".format(pc*gc, "pt"))

        return ret

def test_defaults():
    n = Node()
    assert n.pos == pt(0,0)

def test_tikz_output():

    fig = Figure()
    n = Node(pos=pt(1,10))
    writer = TikzNode()
    assert writer.render(n, fig) == \
        "\\node at ({:.2f}pt, {:.2f}pt) [minimum width={:.2f}pt, minimum height={:.2f}pt];".format(
            (n.pos[0] + n.size[0]/2)*fig.grid[0],
            (n.pos[1] + n.size[1]/2)*fig.grid[1],
            (n.size[0])*fig.grid[0],
            (n.size[1])*fig.grid[1],
            )

def test_tikz_text():
    fig = Figure()
    writer = TikzNode()
    n = Node(text="$testing_the$ text_to_tex")
    assert  writer.render_text(n, fig) == "$testing_the$ text\_to\_tex"

def test_text_size():
    single_line_size = pt(29.011, 0.889)

    fig = Figure()
    t = Text("This is a demonstration text for showing how line breaking works.")
    assert t.size == single_line_size

    t.size = pt(10,1)
    t.sizable = False
    assert t.content_size == pt(10, 4.294)

    t.pad = [pt(1,2), pt(3,1)]
    assert t.size == pt(10,1)
    assert t.content_size == pt(6, 6.694)

    t.sizable = True
    assert t.size == single_line_size + t.pad[0] + t.pad[1]
    assert t.content_size == single_line_size

    t.size *= 2
    assert t.pad == [pt(9.253,4.593), pt(27.758,2.296)]

    # print(t.pad)

def test_hierarchy():
    single_line_size = pt(29.011, 0.889)

    n = HierNode(draw=True)
    n['text'] = Text("This is a demonstration text for showing how line breaking works.")

    tikz = n._writer.render(n, Figure())
    assert tikz == r"""\node at (0.00pt, 0.00pt) [draw,minimum width=0.00pt, minimum height=0.00pt];
\node at (14.51pt, 4.44pt) [minimum width=29.01pt, minimum height=8.89pt] {This is a demonstration text for showing how line breaking works.};"""

    n.sizable=True
    assert n.size == single_line_size

    n.pad = [pt(1,2), pt(3,1)]
    assert n.size == pt(33.011,3.889)

    # print(tikz)

# test_hierarchy()
# test_text_size()
# test_tikz_text()
# test_tikz_output()
