import logging
import threading
import time

from gi.repository import Gtk, Gio

from gol_gtk.model import GameOfLifeModel
from gol_gtk.services import quit_, load_file, next_generation
from gol_gtk.widgets.grid import GameOfLiveGrid

logger = logging.getLogger(__name__)


class GameOfLiveGtk(Gtk.Window):

    _model = None
    _sleep = .1
    _run = False
    _game_thread = None

    _widget_grid = None
    _widget_header_bar = None

    def __init__(self, title, *args, **kwargs):
        Gtk.Window.__init__(self, title=title)

        super(GameOfLiveGtk, self).__init__(*args, **kwargs)

        self.set_border_width(10)
        self.connect('destroy', lambda _: quit_())

        self._model = GameOfLifeModel(cols=50, rows=50, grid_data=[False for _ in range(50 * 50)])

        self.init_header_bar()
        self.init_grid()

        self.show_all()

        self.start()

    def init_header_bar(self):
        self._widget_header_bar = Gtk.HeaderBar()
        self._widget_header_bar.set_show_close_button(True)
        self._widget_header_bar.props.title = self.get_title()

        # Add file open button
        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="document-open-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        self._widget_header_bar.pack_start(button)
        button.connect('clicked', self.on_file_open)

        self.set_titlebar(self._widget_header_bar)

    def init_grid(self):
        self._widget_grid = GameOfLiveGrid(data_provider=self._model)

        self.add(self._widget_grid)

    def on_file_open(self, widget):
        dialog = Gtk.FileChooserDialog(
            "Please choose a file",
            self,
            Gtk.FileChooserAction.OPEN,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, Gtk.STOCK_OPEN, Gtk.ResponseType.OK)
        )

        # Add filters
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            load_file(filename=dialog.get_filename(), model=self._model)
        elif response == Gtk.ResponseType.CANCEL:
            logger.debug('File choose cancelled')

        dialog.destroy()

    def start(self):

        def calculate_generations_loop():
            while True:
                next_generation(model=self._model)

                logger.debug('Calculate generation: {}'.format(self._model.generation))

                time.sleep(self._sleep)

        self._game_thread = threading.Thread(target=calculate_generations_loop)
        self._game_thread.daemon = True
        self._game_thread.start()
