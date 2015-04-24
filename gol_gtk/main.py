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
    _sleep = 1
    _run = False
    _game_thread = None

    _start_stop_button_image_play = Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON)
    _start_stop_button_image_pause = Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PAUSE, Gtk.IconSize.BUTTON)

    _widget_grid = None
    _widget_header_bar = None

    def __init__(self, title, *args, **kwargs):
        Gtk.Window.__init__(self, title=title)

        # super(GameOfLiveGtk, self).__init__(*args, **kwargs)

        self.set_border_width(6)
        self.set_resizable(False)
        self.connect('destroy', lambda _: quit_())

        self._model = GameOfLifeModel(cols=50, rows=50, grid_data=[False for _ in range(50 * 50)])

        self.init_window()

        self.show_all()

    def init_window(self):
        header_bar = self.init_header_bar()
        self.set_titlebar(header_bar)

        # Add file open button
        header_bar.pack_start(self.init_file_open_button())

        # Add play/pause button
        header_bar.pack_start(self.init_play_pause_button())

        # Add reset button
        header_bar.pack_start(self.init_reset_button())

        gol_grid = self.init_gol_grid()

        grid = Gtk.Grid()
        grid.set_column_spacing(6)
        grid.set_row_spacing(6)

        grid.attach(gol_grid, 0, 0, 4, 1)

        grid.attach(self.init_generation_label(), 0, 1, 1, 1)
        grid.attach(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), 1, 1, 1, 1)
        grid.attach(Gtk.Label.new('Speed: '), 2, 1, 1, 1)
        grid.attach(self.init_speed_slider(), 3, 1, 1, 1)

        grid.attach(Gtk.Label.new('Rows: '), 0, 2, 1, 1)
        grid.attach(self.init_rows_input(), 1, 2, 1, 1)
        grid.attach(Gtk.Label.new('Columns: '), 2, 2, 1, 1)
        grid.attach(self.init_cols_input(), 3, 2, 1, 1)

        self.add(grid)

    def init_rows_input(self):
        row_entry = Gtk.Entry()
        row_entry.set_text(str(self._model.rows))
        self._model.connect('notify::rows', self.on_rows_update, row_entry)
        return row_entry

    def init_cols_input(self):
        cols_entry = Gtk.Entry()
        cols_entry.set_text(str(self._model.cols))
        self._model.connect('notify::cols', self.on_cols_update, cols_entry)
        return cols_entry

    def init_header_bar(self):
        header_bar = Gtk.HeaderBar()
        header_bar.set_show_close_button(True)
        header_bar.props.title = self.get_title()

        return header_bar

    def init_play_pause_button(self):
        button = Gtk.Button.new()
        image = Gtk.Image.new_from_stock(Gtk.STOCK_MEDIA_PLAY, Gtk.IconSize.BUTTON)
        button.set_image(image)
        button.connect('clicked', self.on_play_pause_clicked)

        return button

    def init_file_open_button(self):
        button = Gtk.Button.new()
        image = Gtk.Image.new_from_stock(Gtk.STOCK_OPEN, Gtk.IconSize.BUTTON)
        button.set_image(image)
        button.connect('clicked', self.on_file_open)

        return button

    def init_reset_button(self):
        button = Gtk.Button.new()
        image = Gtk.Image.new_from_stock(Gtk.STOCK_REFRESH, Gtk.IconSize.BUTTON)
        button.set_image(image)
        button.connect('clicked', self.on_refresh_button_clicked)

        return button

    def init_gol_grid(self):
        gol_grid = GameOfLiveGrid(data_provider=self._model)

        return gol_grid

    def init_speed_slider(self):
        adjustment = Gtk.Adjustment(1, 0.1, 5, 0.1)

        slider = Gtk.Scale.new(Gtk.Orientation.HORIZONTAL, adjustment)
        slider.connect('value-changed', self.on_speed_slider_value_changed)

        return slider

    def init_generation_label(self):
        text = 'Generation: {}'

        label = Gtk.Label()
        label.set_text(text.format('0'))

        self._model.connect('notify::generation', self.on_generation_update, label, text)

        return label

    def on_speed_slider_value_changed(self, scale_widget):
        self._sleep = scale_widget.get_value()

    def on_rows_update(self, model, rows, input_widget):
        input_widget.set_text(str(model.rows))

    def on_cols_update(self, model, cols, input_widget):
        input_widget.set_text(str(model.cols))

    def on_generation_update(self, model, generation, label_widget, text):
        label_widget.set_text(text.format(model.generation))

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

    def on_refresh_button_clicked(self, widget):
        cols = self._model.cols
        rows = self._model.rows

        grid_data = [False for _ in range(cols * rows)]

        self._model.reset(cols=cols, rows=rows, grid_data=grid_data)

    def on_play_pause_clicked(self, widget):
        if self._run:
            self.stop()
            widget.set_image(self._start_stop_button_image_play)
        else:
            self.start()
            widget.set_image(self._start_stop_button_image_pause)

    def start(self):

        def calculate_generations_loop():
            while self._run:
                next_generation(model=self._model)

                logger.debug('Calculate generation: {}'.format(self._model.generation))

                time.sleep(self._sleep)

        self._run = True

        self._game_thread = threading.Thread(target=calculate_generations_loop)
        self._game_thread.daemon = True
        self._game_thread.start()

    def stop(self):

        self._run = False
