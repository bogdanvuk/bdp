from bdp.point import Point as pt
from bdp.prototype import CallablePrototype
from bdp.figure import fig
from bdp.latex_server import latex_server
from bdp.tikz_writer import TikzQueryTextSize

class Text(CallablePrototype):

    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.pos = pt(0,0)
        self.sizable = True
        self.size = pt(0,0)
        self.text = text
        self._query_writer = TikzQueryTextSize()

    def _get_text_size(self):
        latex_node = self._query_writer.render(self, fig)
        size = latex_server.get_node_size(latex_node)
        for i in range(2):
            size[i] /= fig.grid[i]

        return size

    @property
    def size(self):
        # if self.sizable:
        return self._get_text_size()
        # else:
        #     return self._size

    @size.setter
    def size(self, value):
        self._size = value
