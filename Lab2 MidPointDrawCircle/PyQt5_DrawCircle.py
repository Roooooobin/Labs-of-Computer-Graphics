import math
import sys
from PyQt5.QtWidgets import (QApplication, QWidget)
from PyQt5.QtGui import (QPainter, QPen, QPixmap)
from PyQt5.QtCore import Qt


class DrawCircle(QWidget):

    def __init__(self):
        super(DrawCircle, self).__init__()
        self.board = QPixmap(1000, 500)
        self.board.fill(Qt.white)
        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)
        self.painter = QPainter()
        # 设置起点和终点，并设置标志位以控制打点
        self.radius = 0
        self.center_x = 0
        self.center_y = 0
        self.center_flag = False
        self.xr = 0
        self.yr = 0

    def paintEvent(self, paintEvent):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, self.board)
        self.painter.end()

    def paintPoints(self, x, y):
        self.paintPoint(self.center_x + x, self.center_y + y)
        self.paintPoint(self.center_x - x, self.center_y + y)
        self.paintPoint(self.center_x + x, self.center_y - y)
        self.paintPoint(self.center_x - x, self.center_y - y)
        self.paintPoint(self.center_x + y, self.center_y + x)
        self.paintPoint(self.center_x - y, self.center_y + x)
        self.paintPoint(self.center_x + y, self.center_y - x)
        self.paintPoint(self.center_x - y, self.center_y - x)

    def paintPoint(self, x, y):
        self.painter.begin(self.board)
        self.painter.setPen(QPen(Qt.black, 6))
        self.painter.drawPoint(x, y)
        self.painter.end()
        self.update()

    def mouseMoveEvent(self, event):
        if not self.center_flag:
            self.center_x = event.pos().x()
            self.center_y = event.pos().y()
            self.paintPoint(self.center_x, self.center_y)
            self.center_flag = True
        else:
            self.xr = event.pos().x()
            self.yr = event.pos().y()
            self.radius = math.sqrt((self.xr - self.center_x) ** 2 + (self.yr - self.center_y) ** 2)
            self.midPointDrawCircle()

    def clearBoard(self):
        self.board.fill(Qt.white)
        self.update()
        # 回到初始状态
        self.center_x = 0
        self.center_y = 0
        self.radius = 0
        self.center_flag = False
        self.xr = 0
        self.yr = 0

    def mouseDoubleClickEvent(self, event):
        self.clearBoard()

    def midPointDrawCircle(self):
        x = 0
        y = self.radius
        delta = 1 - self.radius
        self.paintPoints(x, y)
        while x < y:
            if delta < 0:
                delta += (2 * x + 3)
            else:
                delta += (2 * (x - y) + 5)
                y -= 1
            x += 1
            self.paintPoints(x, y)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    drawCircle = DrawCircle()
    drawCircle.show()
    app.exec_()
