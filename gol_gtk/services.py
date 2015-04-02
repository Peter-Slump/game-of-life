import logging

from gi.repository import Gtk

from gol import calculate_next_generation

logger = logging.getLogger(__name__)


def quit_():
    logger.debug('Quit')

    Gtk.main_quit()


def next_generation(model):
    model.next_generation(calculate_next_generation(rows=model.rows,
                                                    cols=model.cols,
                                                    cells=model.grid_data))


def load_file(filename, model):
        cols = None
        rows = 0
        cells = []

        file = open(filename)

        for line in file:
            line = line.strip()
            if cols is None:
                cols = len(line)
            else:
                assert cols == len(line)

            cells += [x == 'X' for x in line]
            rows += 1

        model.reset(cols=cols, rows=rows, grid_data=cells)