from unittest import TestCase

import mock

from gol_gtk.model import GameOfLifeModel


class GameOfLifModelTestCase(TestCase):

    def test(self):
        """
        Case: A model is created and a first generation is given
        Expected:
            - The generation counter is increased
            - The grid data is updated
            - The appropriated events are dispatched
        """

        grid_data_event_callback = mock.MagicMock()
        generation_event_callback = mock.MagicMock()

        model = GameOfLifeModel(rows=2, cols=2, grid_data=[False for _ in range(4)])

        model.connect('notify::grid-data', grid_data_event_callback)
        model.connect('notify::generation', generation_event_callback)

        current_generation = model.generation

        model.next_generation([False, True, False, False])

        self.assertEqual(model.generation, current_generation + 1)
        self.assertEqual(model.grid_data, [False, True, False, False])

        self.assertEqual(grid_data_event_callback.call_count, 1)
        self.assertEqual(generation_event_callback.call_count, 1)

    def test_wrong_grid_size(self):

        model = GameOfLifeModel()  # empty grid

        with self.assertRaises(AssertionError):
            model.next_generation([False, True, False, False, False])

    def test_reset(self):
        """
        Case: A model get reset
        Expected: The values are set to the reset values and the generation is set to 0
        """

        model = GameOfLifeModel(rows=2, cols=2, grid_data=[False for _ in range(4)])

        self.assertEqual(model.rows, 2)
        self.assertEqual(model.cols, 2)
        self.assertEqual(model.grid_data, [False, False, False, False])
        self.assertEqual(model.generation, 0)

        model.reset()  # Reset to empty state

        self.assertEqual(model.rows, 0)
        self.assertEqual(model.cols, 0)
        self.assertEqual(model.grid_data, [])
        self.assertEqual(model.generation, 0)

        model.reset(rows=3, cols=3, grid_data=[False for _ in range(9)])

        self.assertEqual(model.rows, 3)
        self.assertEqual(model.cols, 3)
        self.assertEqual(model.grid_data, [False, False, False, False, False, False, False, False, False])
        self.assertEqual(model.generation, 0)