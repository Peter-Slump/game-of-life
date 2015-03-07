#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""An implementation of Conway's "Game of life"

The grid is handled as a flat list together with dimension properties.

Usage:
Create a file which specifies a pattern with . (dots) and X-es.

Example:

..........
..........
..XX......
...XX.....
..X.......
..........
..........
..........
..........
..........

Run with:

    python gol.py <filename>
"""
__author__ = 'Peter Slump <peter@yarf.nl>'
__license__ = 'MIT'
__version__ = '$Revision$'

def calculate_next_generation(rows, cols, cells):
    """Calculate next generation based on given cells. This function returns
    also a list of cells which it's easy to add again.
    """
    return tuple(get_new_state(i, rows, cols, cells) for i, _ in enumerate(cells))


def get_new_state(index, rows, cols, cells):
    """Calculate the new state of a cell in a next generation.

    ----
    Test all rules for the center cell.
    ----

    Rule One: Any live cell with fewer than two live neighbours dies, as if
    caused by under-population.
    >>> cells = [
    ...    False, False, False,
    ...    False, True,  False,
    ...    True,  False, False
    ... ]
    >>> calculate_new_state(4, 3, 3, cells)
    False

    Rule Two: Any live cell with two or three live neighbours lives on to the
    next generation.
    >>> cells = [
    ...    True,  False, False,
    ...    False, True,  False,
    ...    True,  False, False
    ... ]
    >>> calculate_new_state(4, 3, 3, cells)
    True

    >>> cells = [
    ...    True,  False, False,
    ...    False, True,  True,
    ...    True,  False, False
    ... ]
    >>> calculate_new_state(4, 3, 3, cells)
    True

    Rule Three: Any live cell with more than three live neighbours dies, as if
    by overcrowding.
    >>> cells = [
    ...    True,  False, True,
    ...    False, True,  False,
    ...    True,  False, True
    ... ]
    >>> calculate_new_state(4, 3, 3, cells)
    False

    Any dead cell with exactly three live neighbours becomes a live cell, as if
    by reproduction.
    >>> cells = [
    ...    True,  False, True,
    ...    False, False, False,
    ...    True,  False, False
    ... ]
    >>> calculate_new_state(4, 3, 3, cells)
    True

    >>> cells = [
    ...    True,  False, False,
    ...    False, False, False,
    ...    True,  False, False
    ... ]
    >>> calculate_new_state(4, 3, 3, cells)
    False

    >>> cells = [
    ...    True,  False, True,
    ...    False, False, False,
    ...    True,  False, True
    ... ]
    >>> calculate_new_state(4, 3, 3, cells)
    False

    ----
    Test All rules for the upper left cell
    ----

    Rule One: Any live cell with fewer than two live neighbours dies, as if
    caused by under-population.
    >>> cells = [
    ...    True,  False, False,
    ...    False, False, True,
    ...    False, False, False
    ... ]
    >>> calculate_new_state(0, 3, 3, cells)
    False

    Rule Two: Any live cell with two or three live neighbours lives on to the
    next generation.
    >>> cells = [
    ...    True,  False, False,
    ...    False, False, True,
    ...    False, False, True
    ... ]
    >>> calculate_new_state(0, 3, 3, cells)
    True

    >>> cells = [
    ...    True,  True,  False,
    ...    False, False, True,
    ...    False, False, True
    ... ]
    >>> calculate_new_state(0, 3, 3, cells)
    True

    Rule Three: Any live cell with more than three live neighbours dies, as if
    by overcrowding.
    >>> cells = [
    ...    True,  False, False,
    ...    False, True,  True,
    ...    False, True,  True
    ... ]
    >>> calculate_new_state(0, 3, 3, cells)
    False

    Rule Four: Any dead cell with exactly three live neighbours becomes a live
    cell, as if by reproduction.
    >>> cells = [
    ...    False, False, False,
    ...    False, True, False,
    ...    False, True, True
    ... ]
    >>> calculate_new_state(0, 3, 3, cells)
    True

    >>> cells = [
    ...    False, False, False,
    ...    False, False, True,
    ...    False, False, True
    ... ]
    >>> calculate_new_state(0, 3, 3, cells)
    False

    >>> cells = [
    ...    False, False, False,
    ...    False, True,  True,
    ...    False, True,  True
    ... ]
    >>> calculate_new_state(0, 3, 3, cells)
    False

    ----
    Test all rules for the lower right cell
    ----
    Rule One: Any live cell with fewer than two live neighbours dies, as if
    caused by under-population.
    >>> cells = [
    ...    False, True, False,
    ...    False, False, False,
    ...    False, False, True
    ... ]
    >>> calculate_new_state(8, 3, 3, cells)
    False

    Rule Two: Any live cell with two or three live neighbours lives on to the
    next generation.
    >>> cells = [
    ...    False, True, False,
    ...    False, True, False,
    ...    False, False, True
    ... ]
    >>> calculate_new_state(8, 3, 3, cells)
    True

    >>> cells = [
    ...    False,  True, False,
    ...    False, True,  False,
    ...    True,  False, True
    ... ]
    >>> calculate_new_state(8, 3, 3, cells)
    True

    Rule Three: Any live cell with more than three live neighbours dies, as if
    by overcrowding.
    >>> cells = [
    ...    True,  True,  False,
    ...    True,  True,  False,
    ...    False, False, True
    ... ]
    >>> calculate_new_state(8, 3, 3, cells)
    False

    Any dead cell with exactly three live neighbours becomes a live cell, as if
    by reproduction.
    >>> cells = [
    ...    False, True,  False,
    ...    True,  True,  False,
    ...    False, False, False
    ... ]
    >>> calculate_new_state(8, 3, 3, cells)
    True

    >>> cells = [
    ...    False, True, False,
    ...    False, False, False,
    ...    False, True, False
    ... ]
    >>> calculate_new_state(8, 3, 3, cells)
    False

    >>> cells = [
    ...    True,  True,  False,
    ...    True,  True,  False,
    ...    False, False, False
    ... ]
    >>> calculate_new_state(8, 3, 3, cells)
    False

    ----
    Test non-square field
    ----
    >>> cells = [
    ...    False, False, False, False,
    ...    False, False, False, True,
    ...    False, False, True,  True
    ... ]
    >>> calculate_new_state(11, 3, 4, cells)
    True
    """

    number_alive = 0

    # Calculate in which row and column we currently are
    current_row = index / cols
    current_col = index % cols

    # Loop through the rows from above to below current row
    for cursor_row in range(current_row - 1, current_row + 2):
        # Loop through the columns from left until right current column
        for cursor_col in range(current_col - 1, current_col + 2):
            # Calculate the list-index and keep in mind that it is an
            # torodial array (when you get of the grid you will enter
            # at the other side)
            cursor_index = (cursor_row % rows) * cols + (cursor_col % cols)
            # Increase number if cell is alive and it's not the current cell
            if cursor_index != index and cells[cursor_index]:
                number_alive += 1

                if number_alive > 3:
                    break
        if number_alive > 3:
                    break

    return number_alive == 3 or (cells[index] and number_alive == 2)

if __name__ == '__main__':
    import os
    import time
    import fileinput

    cols = None
    rows = 0
    cells = []
    for line in fileinput.input():
        line = line.strip()
        if cols is None:
            cols = len(line)
        else:
            assert cols == len(line)

        cells += [x == 'X' for x in line]
        rows += 1

    generation = 0

    while True:
        os.system('clear')

        generation += 1
        line = []
        print u' ' + (u'-' * cols)
        for index, cell in enumerate(cells):
            line.append(u'⚫' if cell else u' ')
            if (index + 1) % cols == 0:
                print u'|' + u''.join(line) + u'|'
                line = []
        print u' ' + (u'-' * cols)
        print u'Rows: {}, Columns: {}, Generation: {}'.format(rows, cols,
                                                              generation)
        time.sleep(.01)

        cells = calculate_next_generation(rows, cols, cells)
