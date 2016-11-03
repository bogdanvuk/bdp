from bdp.point import Point as pt
from bdp.prototype import CallablePrototype
from bdp.figure import fig
from bdp.latex_server import latex_server, TikzSyntaxError
from bdp.tikz_writer import TikzQueryTextSize
from bdp.node import SizableNodeBase

class Text(SizableNodeBase):

    def __init__(self, text="", **kwargs):
        super().__init__(**kwargs)
        self.sizable = True
        self.text = text
        self._query_writer = TikzQueryTextSize()

    def _get_text_size(self):
        latex_node = self._query_writer.render(self, fig)
        try:
            size = latex_server.get_node_size(latex_node)
        except TikzSyntaxError:
            raise TikzSyntaxError("Tikz syntax for the text node is invalid due to some of its attributes' settings.")
        for i in range(2):
            size[i] /= fig.grid[i]

        return size

    @property
    def content_size(self):
        # if self.sizable:
        return self._get_text_size()
        # else:
        #     return self._size

