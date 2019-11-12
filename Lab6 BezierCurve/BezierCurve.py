import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget)
from PyQt5.QtGui import (QPainter, QPen, QPixmap)
from PyQt5.QtCore import Qt


class BezierCurve(QWidget):

    def __init__(self):
        super(BezierCurve, self).__init__()
        self.resize(800, 600)
        self.board = QPixmap(800, 600)
        self.board.fill(Qt.white)
        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)
        self.painter = QPainter()
        self.control_vertexes = []

    def paintEvent(self, paintEvent):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, self.board)
        self.painter.end()

    def paintPoint(self, x, y, color):
        self.painter.begin(self.board)
        self.painter.setPen(QPen(color, 6))
        self.painter.drawPoint(x, y)
        self.painter.end()
        self.update()

    def join_vertexes(self, vertexes, color):
        if len(vertexes) < 3:
            return
        else:
            # 依次连接各点
            for i in range(len(vertexes) - 1):
                self.bresenham_drawline(vertexes[i][0], vertexes[i][1], vertexes[i + 1][0],
                                        vertexes[i + 1][1], color)

    def draw_bezier(self, color):
        if len(self.control_vertexes) == 4:
            x0, y0 = self.control_vertexes[0]
            x1, y1 = self.control_vertexes[1]
            x2, y2 = self.control_vertexes[2]
            x3, y3 = self.control_vertexes[3]
            for t in range(1000):
                t = t / 1000
                x = (1-t)**3 * x0 + 3*t*(1-t)**2 * x1 + 3*t*t*(1-t) * x2 + t**3 * x3
                y = (1-t)**3 * y0 + 3*t*(1-t)**2 * y1 + 3*t*t*(1-t) * y2 + t**3 * y3
                self.paintPoint(x, y, color)
        elif len(self.control_vertexes) == 5:
            x0, y0 = self.control_vertexes[0]
            x1, y1 = self.control_vertexes[1]
            x2, y2 = self.control_vertexes[2]
            x3, y3 = self.control_vertexes[3]
            x4, y4 = self.control_vertexes[4]
            for t in range(1000):
                t = t / 1000
                x = (1-t)**4 * x0 + 4*t*(1-t)**3 * x1 + 6*t*t*(1-t)**2 * x2 + 4*t*t*t*(1-t) * x3 + t**4 * x4
                y = (1-t)**4 * y0 + 4*t*(1-t)**3 * y1 + 6*t*t*(1-t)**2 * y2 + 4*t*t*t*(1-t) * y3 + t**4 * y4
                self.paintPoint(x, y, color)
        else:
            return

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if event.buttons() == QtCore.Qt.LeftButton:  # 左键按下
            self.control_vertexes.append((x, y))
            self.paintPoint(x, y, Qt.black)
        elif event.buttons() == QtCore.Qt.RightButton:
            self.join_vertexes(self.control_vertexes, Qt.black)
            self.draw_bezier(Qt.blue)

    # 画板清零，回到初始状态
    def mouseDoubleClickEvent(self, event):
        self.board.fill(Qt.white)
        self.update()
        # 回到初始状态
        self.control_vertexes.clear()

    def bresenham_drawline(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        x = x0
        y = y0
        # 通过两点的位置关系和斜率区分不同情况
        if x1 > x0:
            step_x = 1
        else:
            step_x = -1
        if y1 > y0:
            step_y = 1
        else:
            step_y = -1
        if dy > dx:
            # 斜率绝对值大于1，交换dx, dy再代入公式，并记录交换的标志位
            tmp = dx
            dx = dy
            dy = tmp
            flag_change = True
        else:
            flag_change = False

        delta = 2 * dy - dx
        for i in range(1, dx + 1):
            # 调用封装好的画点函数画点
            self.paintPoint(x, y, color)
            if delta >= 0:
                if flag_change:
                    x += step_x
                else:
                    y += step_y
                delta -= 2 * dx
            if flag_change:
                y += step_y
            else:
                x += step_x
            delta += 2 * dy


if __name__ == "__main__":
    app = QApplication(sys.argv)
    curve_pyqt = BezierCurve()
    curve_pyqt.show()
    app.exec_()
