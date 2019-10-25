import sys
from PyQt5.QtWidgets import (QApplication, QWidget)
from PyQt5.QtGui import (QPainter, QPen, QPixmap)
from PyQt5.QtCore import Qt


class Example(QWidget):

    def __init__(self):
        super(Example, self).__init__()
        self.board = QPixmap(1000, 500)
        self.board.fill(Qt.white)
        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)
        self.painter = QPainter()
        # 设置起点和终点，并设置标志位以控制打点
        self.x0 = 0
        self.y0 = 0
        self.point0_flag = True
        self.x1 = 0
        self.y1 = 0
        self.point1_flag = True

    def paintEvent(self, paintEvent):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, self.board)
        self.painter.end()

    def paintPoint(self, x, y):
        self.painter.begin(self.board)
        self.painter.setPen(QPen(Qt.black, 6))
        self.painter.drawPoint(x, y)
        self.painter.end()
        self.update()

    def mousePressEvent(self, event):
        # 如果起点还未画，画起点
        if self.point0_flag:
            self.x0 = event.pos().x()
            self.y0 = event.pos().y()
            print(self.x0, self.y0)
            self.paintPoint(self.x0, self.y0)
            self.point0_flag = False
        # 如果终点还未画，画终点
        elif self.point1_flag:
            self.x1 = event.pos().x()
            self.y1 = event.pos().y()
            print(self.x1, self.y1)
            self.paintPoint(self.x1, self.y1)
            self.point1_flag = False
        # 起点终点都画好之后再点击，调用Bresenham算法画线
        else:
            self.point1_flag = True
            self.point0_flag = True
            self.BresenhamDrawLine()

    def mouseDoubleClickEvent(self, event):
        self.board.fill(Qt.white)
        self.update()
        # 回到初始状态
        self.x0 = 0
        self.y0 = 0
        self.point0_flag = True
        self.x1 = 0
        self.y1 = 0
        self.point1_flag = True

    def BresenhamDrawLine(self):
        dx = abs(self.x1 - self.x0)
        dy = abs(self.y1 - self.y0)
        print(dx, dy)
        x = self.x0
        y = self.y0
        # 通过两点的位置关系和斜率区分不同情况
        if self.x1 > self.x0:
            step_x = 1
        else:
            step_x = -1
        if self.y1 > self.y0:
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
        for i in range(1, dx+1):
            # 调用封装好的画点函数画点
            self.paintPoint(x, y)
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
    bresenham_pyqt = Example()
    bresenham_pyqt.show()
    app.exec_()
