from bdp.node import Node
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
        "\\node at ({:.2f}pt, {:.2f}pt) [minimum width={:.2f}pt, minimum height={:.2f}pt];\n".format(
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
    fig = Figure()
    t = Text("This is a demonstration text for showing how line breaking works.")
    assert t.size == pt(29.011, 0.889)

    t.size = pt(10,1)
    t.sizable = False
    assert t.size == pt(10, 4.294)

# test_text_size()
# test_tikz_text()
# test_tikz_output()
