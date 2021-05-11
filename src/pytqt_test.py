
'''import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg
import numpy as np

app = QApplication(sys.argv)

win = pg.plot()

x = np.arange(10)
y1 = np.sin(x)
y2 = 1.1 * np.sin(x + 1)
y3 = 1.2 * np.sin(x + 2)

bg1 = pg.BarGraphItem(x=x, height=y1, width=0.3, brush='r')
bg2 = pg.BarGraphItem(x=x + 0.33, height=y2, width=0.3, brush='g')
bg3 = pg.BarGraphItem(x=x + 0.66, height=y3, width=0.3, brush='b')

win.addItem(bg1)
win.addItem(bg2)
win.addItem(bg3)


# Final example shows how to handle mouse clicks:
class BarGraph(pg.BarGraphItem):
    def mouseClickEvent(self, event):
        print("clicked")


bg = BarGraph(x=x, y=y1 * 0.3 + 2, height=0.4 + y1 * 0.2, width=0.8)
win.addItem(bg)

status = app.exec_()
sys.exit(status)'''


from PyQt5.QtWidgets import (QApplication, QWidget)
from PyQt5.Qt import Qt
import pyqtgraph as pg
import numpy as np


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()


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
        print('left key pressed')
        x = np.random.normal(size=500)
        y = np.random.normal(size=500)
        pg.plot(x, y, pen=None, symbol='o')


    def right_key(self):
        print('right key pressed')

    def up_key(self):
        print('up key pressed')

    def down_key(self):
        print('down key pressed')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = pg.plot() 

    demo = MainWindow()

    demo.show()

    sys.exit(app.exec_())