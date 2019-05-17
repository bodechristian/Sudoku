from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from UI.SudokuMain import Ui_MainWindow

import numpy as np
import sys
import math
import time


class Point:
    def __init__(self, x_init, y_init):
        self.row = x_init
        self.column = y_init

    def shift(self, x, y):
        self.row += x
        self.column += y

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.row == other.row and self.column == other.column
        return False

    def __repr__(self):
        return "".join(["P(", str(self.row + 1), ",", str(self.column + 1), ")"])


class WindowSudoku(QtWidgets.QMainWindow):
    """
    the main window for the sudoku
    """
    def __init__(self):
        super(WindowSudoku, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.btn_clicked)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()
        if 49 <= e.key() <= 57:
            if legal_next(e.key()-48, cur_loc):
                change_value(e.key()-48, cur_loc)
        if e.key() == Qt.Key_Delete:
            delete_value(cur_loc)
        if e.key() == Qt.Key_Left:
            change_cur_loc(0, -1)
        if e.key() == Qt.Key_Right:
            change_cur_loc(0, 1)
        if e.key() == Qt.Key_Up:
            change_cur_loc(-1, 0)
        if e.key() == Qt.Key_Down:
            change_cur_loc(1, 0)

    @staticmethod
    def btn_clicked():
        start_time = time.time()
        solve()
        print(f'Time it took to solve the Sudoku: {time.time() - start_time} seconds')


def legal_next(value, loc):
    """

    finds out if the given value is legal in the current sudoku
    :param value: the value that has been entered and is checked for legality
    :param loc: the location of the cell where the value wants to go
    :return: true if the next combination in the sudoku is legal
    """
    if (application.ui.__getattribute__(f'cell{loc.column+1}{loc.row+1}')).text() != "":
        return False
    if value in sudoku_grid[:, loc.column]:
        return False
    if value in sudoku_grid[loc.row]:
        return False
    i_offset = math.floor(loc.row / 3)
    j_offset = math.floor(loc.column / 3)
    for i in range(3):
        for j in range(3):
            if Point(i + 3*i_offset, j + 3*j_offset) != loc and sudoku_grid[i + 3*i_offset, j + 3*j_offset] == value:
                return False
    return True


def change_value(value, loc):
    """
    Takes the given value and attempts to put it in the cell that is given
    :param value: the value to be entered in the given cell
    :param loc: the location of the cell where the value goes
    """
    (application.ui.__getattribute__(f'cell{loc.column+1}{loc.row+1}')).setText(str(value))
    sudoku_grid[loc.row, loc.column] = value
    global cnt_free_cells
    cnt_free_cells -= 1
    # print(f'Placed {value} at {loc}')


def delete_value(loc):
    """
    Deletes the value at the given location

    :param loc: of the value that is to be deleted
    """
    (application.ui.__getattribute__(f'cell{loc.column+1}{loc.row+1}')).setText("")
    sudoku_grid[loc.row, loc.column] = 0
    global cnt_free_cells
    cnt_free_cells += 1


def change_cur_loc(row_change, column_change):
    """
    Changes the current location to an adjacent cell
    :param row_change: (-1, 0, 1) symbolises change on vertical axis
    :param column_change: (-1, 0, 1) symbolises change on horizontal axis
    """
    (application.ui.__getattribute__(f'cell{cur_loc.column+1}{cur_loc.row+1}')).setStyleSheet('')
    if (row_change == 1 and cur_loc.row < 8) or (row_change == -1 and cur_loc.row > 0):
        cur_loc.row = cur_loc.row + row_change
    if (column_change == 1 and cur_loc.column < 8) or (column_change == -1 and cur_loc.column > 0):
        cur_loc.column = cur_loc.column + column_change
    (application.ui.__getattribute__(f'cell{cur_loc.column+1}{cur_loc.row+1}'))\
        .setStyleSheet('background-color: #CBACEF')


def solve():
    """
    Solves the Sudoku
    """
    make_free_cell_list()
    # print(lst_free_cells)
    stop = False
    ret_val = 0
    while not stop:
        temp_val = test_cell(ret_val)
        ret_val += temp_val
        if temp_val == 5:
            stop = True
    print(f'Done solving')
    print(f'Times a cell has been tested: {cell_cnt}')


def make_free_cell_list():
    """
    Goes through the UI and saves the cells with no entries in the global list lst_free_cells
    """
    for row in range(9):
        for col in range(9):
            if (application.ui.__getattribute__(f'cell{col+1}{row+1}')).text() == "":
                lst_free_cells.append(Point(row, col))


def test_cell(index):
    """
    Tests a cell from the list of free cells (lst_free_cells) whether the next number is legal in that cell
    :param index: the current index in the list of free cells
    :return: -1: go to previous cell (1-9 has been tested, none are legal)
              0: stay in this cell (test the next number in future iteration)
              1: go to next cell (legal number for this cell has been found)
              5: stop algorithm (either first cell has no legal number or solution has been found)
    """
    global cell_cnt
    cell_cnt += 1
    loc = lst_free_cells[index]
    cell_text = (application.ui.__getattribute__(f'cell{loc.column+1}{loc.row+1}')).text()
    # print(f'starting to test {cell_text} at {loc}')
    if cell_text == "":  # no value in the cell yet
        val = 1
    elif 0 < int(cell_text) < 9:  # value in the cell, get the next higher number to test
        delete_value(loc)
        val = int(cell_text) + 1
    else:  # cell contains 9, so go back, if at first cell -> not solvable
        if index == 0:
            print("Go solution")
            return 5
        else:
            print(f'No legal move at '
                  f'{loc}')
            delete_value(loc)
            return -1
    if legal_next(val, loc):
        change_value(val, loc)
        if index == len(lst_free_cells) - 1:
            # done solving
            return 5
        else:
            print(f'Placed {val} at {loc}')
            return 1
    else:
        change_value(val, loc)
        return 0


def import_sudoku(lst_temp):
    """
    imports the sudoku in the given list
    """
    temp_index = 0
    for row in range(9):
        for col in range(9):
            val = lst_temp[temp_index]
            if val != 0:
                change_value(val, Point(row, col))
            temp_index += 1


"""
initializing window
"""
app = QtWidgets.QApplication([sys.argv])
application = WindowSudoku()


"""
initializing variables
"""
sudoku_grid = np.zeros((9, 9))
cur_loc = Point(0, 0)
lst_free_cells = []
cnt_free_cells = 81

lst_import = [4,7,0,0,0,0,6,0,8,
              0,6,2,0,0,0,0,4,0,
              0,0,0,0,0,4,2,0,1,
              8,9,0,5,0,6,0,3,7,
              0,0,6,0,0,0,8,0,5,
              0,0,0,0,0,1,0,0,2,
              9,0,0,0,0,0,5,8,0,
              6,8,7,0,0,0,0,0,0,
              0,5,0,0,6,3,0,0,0]
change_cur_loc(0, 0)  # essentially only to set the colour, so that user sees what cell is selected
import_sudoku(lst_import)
cell_cnt = 0

"""
showing window
"""
application.show()
sys.exit(app.exec())
