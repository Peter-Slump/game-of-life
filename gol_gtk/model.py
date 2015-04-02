import logging

from gi.repository import GObject

logger = logging.getLogger(__name__)


class GameOfLifeModel(GObject.GObject):

    cols = GObject.property(type=GObject.TYPE_INT, default=0, flags=GObject.PARAM_READWRITE)
    rows = GObject.property(type=GObject.TYPE_INT, default=0, flags=GObject.PARAM_READWRITE)
    grid_data = GObject.property(type=GObject.TYPE_PYOBJECT, flags=GObject.PARAM_READWRITE)
    generation = GObject.property(type=GObject.TYPE_INT, default=0, flags=GObject.PARAM_READWRITE)

    def __init__(self, cols=0, rows=0, grid_data=list()):
        GObject.GObject.__init__(self)

        self.reset(cols=cols, rows=rows, grid_data=grid_data)

    def next_generation(self, grid_data):
        """Populate with data for the next generation.

        This increases the generation counter.
        """
        assert len(grid_data) == self.rows * self.cols

        self.set_property('grid_data', grid_data)
        self.set_property('generation', self.get_property('generation') + 1)

    def reset(self, cols=0, rows=0, grid_data=list()):
        """Reset to given or empty state."""
        self.set_property('cols', cols)
        self.set_property('rows', rows)
        self.set_property('grid_data', grid_data)
        self.set_property('generation', 0)