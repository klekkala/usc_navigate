import sys
import random
import matplotlib
matplotlib.use('Qt5Agg')
from PyQt5.Qt import Qt
import beogym as bo
import data_helper as dh

from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, prev, curr, o):

        self.agents_pos_prev = prev
        self.agents_pos_curr = curr
        self.o = o
        super(MainWindow, self).__init__()

        self.canvas = MplCanvas(self, width=5, height=4, dpi=100)
        self.setCentralWidget(self.canvas)

        self.xdata = []
        self.ydata = []
        self.update_plot(self.agents_pos_prev[0], self.agents_pos_prev[1])
        self.update_plot(self.agents_pos_curr[0], self.agents_pos_curr[1])

        self.show()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.left_key()
        if event.key() == Qt.Key_Right:
            self.right_key()
        if event.key() == Qt.Key_Up:
            self.up_key()
        if event.key() == Qt.Key_Down:
            self.down_key()

    def left_key(self):
        print("the arguments are", self.agents_pos_curr, self.agents_pos_prev,)
        agents_pos_next = bo.go_left(self.agents_pos_curr, self.agents_pos_prev, self.o)
        self.agents_pos_prev = self.agents_pos_curr
        self.agents_pos_curr  = agents_pos_next[0]
        self.update_plot(self.agents_pos_curr[0], self.agents_pos_curr[1])

    def right_key(self):
        print("the arguments are", self.agents_pos_curr, self.agents_pos_prev,)
        agents_pos_next = bo.go_right(self.agents_pos_curr, self.agents_pos_prev, self.o)
        self.agents_pos_prev = self.agents_pos_curr
        self.agents_pos_curr  = agents_pos_next[0]
        self.update_plot(self.agents_pos_curr[0], self.agents_pos_curr[1])

    def up_key(self):
        print("the arguments are", self.agents_pos_curr, self.agents_pos_prev,)
        agents_pos_next = bo.go_straight(self.agents_pos_curr, self.agents_pos_prev, self.o)
        self.agents_pos_prev = self.agents_pos_curr
        self.agents_pos_curr  = agents_pos_next[0]
        self.update_plot(self.agents_pos_curr[0], self.agents_pos_curr[1])

    def down_key(self):
        print("the arguments are", self.agents_pos_curr, self.agents_pos_prev,)
        agents_pos_next = bo.go_back(self.agents_pos_curr, self.agents_pos_prev, self.o)
        self.agents_pos_prev = self.agents_pos_curr
        self.agents_pos_curr  = agents_pos_next[0]
        self.update_plot(self.agents_pos_curr[0], self.agents_pos_curr[1])

    def update_plot(self, x, y):
        # Drop off the first y element, append a new one.
        self.ydata = self.ydata + [x]
        self.xdata = self.xdata + [y]

        self.canvas.axes.cla()  # Clear the canvas.
        self.canvas.axes.plot(self.xdata, self.ydata, '-o')
        # Trigger the canvas to update and redraw.
        self.canvas.draw()


def main():
    o = dh.dataHelper()
    o.read_routes()
    prev = o.reset()
    print("image_name prev", o.image_name(prev))
    agents_pos_1 = o.find_next(prev)[0]
    print("image_name curr", o.image_name(agents_pos_1))
    print("agents_pos", agents_pos_1)
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow(prev, agents_pos_1, o)
    app.exec_()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()