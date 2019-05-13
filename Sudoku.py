from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from UI.SudokuMain import Ui_MainWindow

import sys
import math


class Point:
    def __init__(self, x_init, y_init):
        self.row = x_init
        self.column = y_init

    def shift(self, x, y):
        self.row += x
        self.column += y

    def __repr__(self):
        return "".join(["P(", str(self.row+1), ",", str(self.column+1), ")"])


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
            change_value(str(e.key()-48), cur_loc.row, cur_loc.column)
        if e.key() == Qt.Key_Left:
                change_cur_loc(0, -1)
        if e.key() == Qt.Key_Right:
                change_cur_loc(0, 1)
        if e.key() == Qt.Key_Up:
                change_cur_loc(-1, 0)
        if e.key() == Qt.Key_Down:
                change_cur_loc(1, 0)

    def btn_clicked(self):
        self.ui.TEST.setText(str(self.ui.centralwidget.geometry()))
        solve()


def legal_next(value, row, column):
    """
    finds out if the given value is legal in the current sudoku
    :param value: the value that has been entered and is checked for legality
    :param row: the values row [1..8]
    :param column: the values column [1..8]
    :return: true if the next combination in the sudoku is legal
    """

    if value in lsts_col.__getitem__(column):
        return False
    if value in lsts_row.__getitem__(row):
        return False
    block_num = 3 * math.floor(column / 3) + math.floor(row / 3)
    if value in lsts_block.__getitem__(block_num):
        return False
    return True


def change_value(value, row, column):
    """
    Takes the given value and attempts to put it in the cell that is given
    :param value: the value to be entered in the current cell
    :param row: the row of the cell in which the value should go
    :param column: the column of the cell in which the value should go
    """
    (application.ui.__getattribute__(f'cell{column+1}{row+1}')).setText(str(value))
    (lsts_row.__getitem__(row)).append(value)
    (lsts_col.__getitem__(column)).append(value)
    block_num = 3 * math.floor(column / 3) + math.floor(row / 3)
    (lsts_block.__getitem__(block_num)).append(value)
    global cnt_free_cells
    cnt_free_cells -= 1
    print(f'Placed {value} at ({row+1},{column+1})')


def delete_value(loc):
    value = (application.ui.__getattribute__(f'cell{loc.column+1}{loc.row+1}')).text()
    (application.ui.__getattribute__(f'cell{loc.column+1}{loc.row+1}')).setText("")
    (lsts_row.__getitem__(loc.row)).remove(int(value))
    (lsts_col.__getitem__(loc.column)).remove(int(value))
    block_num = 3 * math.floor(loc.column / 3) + math.floor(loc.row / 3)
    (lsts_block.__getitem__(block_num)).remove(int(value))
    global cnt_free_cells
    cnt_free_cells += 1
    #print(f'Removed {value} at ({loc.row+1},{loc.column+1})')


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
    make_free_cell_list()
    print(lst_free_cells)
    test_cell(0)
    print(f'done')


def make_free_cell_list():
    for row in range(9):
        for col in range(9):
            if (application.ui.__getattribute__(f'cell{col+1}{row+1}')).text() == "":
                lst_free_cells.append(Point(row, col))


def test_cell(index):
    global rc_cnt
    rc_cnt += 1
    print(rc_cnt)
    loc = lst_free_cells.__getitem__(index)
    cell_text = (application.ui.__getattribute__(f'cell{loc.column+1}{loc.row+1}')).text()
    #print(f'starting to test {cell_text} at {loc}')
    if cell_text == "":
        val = 1
    elif 0 < int(cell_text) < 9:
        delete_value(loc)
        val = int(cell_text) + 1
    else:
        if index == 0:
            print("no solution")
            return
        else:
            print(f'going back')
            delete_value(loc)
            test_cell(index-1)
    if legal_next(val, loc.row, loc.column):
        change_value(val, loc.row, loc.column)
        if index == len(lst_free_cells) - 1:
            print(f'Done solving')
            for rows in range(9):
                lst_temp = []
                for cols in range(9):
                    lst_temp.append((application.ui.__getattribute__(f'cell{cols+1}{rows+1}')).text())
                print(lst_temp)
        else:
            test_cell(index + 1)
    else:
        change_value(val, loc.row, loc.column)
        test_cell(index)


def import_sudoku(lst_temp):
    """
    imports the sudoku in the given list
    """
    temp_index = 0
    for row in range(9):
        for col in range(9):
            val = lst_temp.__getitem__(temp_index)
            if val != 0:
                change_value(val, row, col)
            temp_index += 1

"""
initializing window
"""
app = QtWidgets.QApplication([sys.argv])
application = WindowSudoku()

lsts_col = [[], [], [], [], [], [], [], [], [], []]
lsts_row = [[], [], [], [], [], [], [], [], [], []]
lsts_block = [[], [], [], [], [], [], [], [], [], []]

cur_loc = Point(0, 0)
lst_free_cells = []
cnt_free_cells = 81

"""
insert random value for cells
for row in range(9):
    for column in range(9):
        change_value(str(random.randint(1, 9)), row, column)
"""
lst_import = [0,0,9,0,1,0,0,4,3,
              6,0,1,4,0,0,0,0,0,
              0,0,0,3,5,0,0,0,6,
              0,0,0,0,0,0,0,9,1,
              0,0,6,0,4,0,8,0,0,
              8,1,0,0,0,0,0,0,0,
              4,0,0,0,7,2,0,0,0,
              0,0,0,0,0,4,7,0,9,
              2,9,0,0,8,0,5,0,0]

"""
initializing variables
if __name__ == '__main__':
    sys.setrecursionlimit(100000)
    threading.stack_size(200000000)
    thread = threading.Thread(target=your_code)
    thread.start()
"""
change_cur_loc(0, 0)
import_sudoku(lst_import)
rc_cnt = 0
sys.setrecursionlimit(10000)
#resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
#resource.setrlimit(resource.RLIMIT_STACK, (2**29,-1))


"""
tests
"""

"""
showing window
"""
application.show()
sys.exit(app.exec())

