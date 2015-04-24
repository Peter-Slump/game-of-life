import logging

from gi.repository import Gdk, Gtk, GObject

logger = logging.getLogger(__name__)


class GameOfLiveGrid(Gtk.DrawingArea):

    # Percentage (0 - 1)
    cell_spacing = GObject.property(type=GObject.TYPE_FLOAT,
                                    default=0.1,
                                    flags=GObject.PARAM_READWRITE)

    # width & height of one cell in pixels
    cell_size = GObject.property(type=GObject.TYPE_INT,
                                 default=10,
                                 flags=GObject.PARAM_READWRITE)

    _data_provider = None

    def __init__(self, data_provider, *args, **kwargs):
        super(GameOfLiveGrid, self).__init__(*args, **kwargs)

        self._init_data_provider(data_provider)

        self.connect('draw', self.on_draw)
        self.connect('configure-event', self.on_configure_event)
        self.connect('button-press-event', self.on_button_press_event)
        self.connect('motion-notify-event', self.on_motion_notify_event)

        # Ask to receive events the drawing area doesn't normally
        # subscribe to
        self.set_events(self.get_events()
                        | Gdk.EventMask.LEAVE_NOTIFY_MASK  # the pointer has left the window.
                        | Gdk.EventMask.BUTTON_PRESS_MASK  # a mouse button has been pressed.
                        | Gdk.EventMask.POINTER_MOTION_MASK  # the pointer (usually a mouse) has moved.
                        | Gdk.EventMask.POINTER_MOTION_HINT_MASK)

    def _init_data_provider(self, data_provider):

        self._data_provider = data_provider

        data_provider.connect('notify::grid-data', self.on_grid_data_update)

    def on_grid_data_update(self, model, gdata_grid_data):
        self.queue_draw()

        return True

    def on_configure_event(self, drawing_area, event):
        logger.debug('configure-event')

        return True

    def on_button_press_event(self, drawing_area, event):
        logger.debug('button-press-event')

        if event.button == 1:
            self.enable_cell_by_position(event.x, event.y)

        return True

    def on_motion_notify_event(self, drawing_area, event):
        (window, x, y, state) = event.window.get_pointer()

        if state & Gdk.ModifierType.BUTTON1_MASK:
            self.enable_cell_by_position(x, y)

        return True

    def on_draw(self, drawing_area, cairo_context):
        logger.debug('Handle Draw-event')

        # Get available width and height of visible drawing area
        width = drawing_area.get_allocated_width()
        height = drawing_area.get_allocated_height()

        cell_spacing = self.cell_spacing
        cell_size = self.cell_size

        cols = self._data_provider.cols
        rows = self._data_provider.rows
        grid_data = self._data_provider.grid_data

        def is_alive(x, y):
            try:
                return grid_data[(cols * y + x)]
            except IndexError:
                return False

        # Calculate spacing size to whole pixel size
        spacing_size = float(cell_size) * cell_spacing
        spacing_size = int(round(spacing_size))

        # Set correct size
        widget_width = (cell_size * cols) + (spacing_size * cols + 1)
        widget_height = (cell_size * rows) + (spacing_size * rows + 1)

        drawing_area.set_size_request(widget_width, widget_height)

        pos_y = spacing_size
        current_row = 0

        while pos_y < height and current_row < rows:
            pos_x = spacing_size
            current_col = 0
            while pos_x < width and current_col < cols:
                if is_alive(current_col, current_row):
                    cairo_context.set_source_rgb(0, 0, 0)
                else:
                    cairo_context.set_source_rgb(1, 1, 1)

                # If we're outside the clip this will do nothing.
                cairo_context.rectangle(pos_x, pos_y,
                                        cell_size,
                                        cell_size)
                cairo_context.fill()

                pos_x += spacing_size + cell_size
                current_col += 1

            pos_y += spacing_size + cell_size
            current_row += 1

        return True

    def enable_cell_by_position(self, x, y):

        # Calculate which cell is underneath the given coordinates
        cell_spacing = self.cell_spacing
        cell_size = self.cell_size

        # Calculate spacing size to whole pixel size
        spacing_size = float(cell_size) * cell_spacing
        spacing_size = int(round(spacing_size))

        pos_x = (x - (cell_spacing * 2)) / (spacing_size + cell_size)
        pos_y = (y - (cell_spacing * 2)) / (spacing_size + cell_size)

        self._data_provider.set_cell_state(pos_x=int(round(pos_x)), pos_y=int(round(pos_y)), state=True)
