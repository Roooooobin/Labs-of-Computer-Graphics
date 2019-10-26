import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget)
from PyQt5.QtGui import (QPainter, QPen, QPixmap)
from PyQt5.QtCore import Qt


class Edge:
    def __init__(self):
        self.x = None  # 与扫描线相交的点的x坐标
        self.dx = None  # 斜率的倒数
        self.y_max = None  # 上端点的y坐标
        self.next = None  # 指向下一条边


class PolygonClip(QWidget):

    def __init__(self):
        super(PolygonClip, self).__init__()
        self.board = QPixmap(1000, 500)
        self.board.fill(Qt.white)
        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)
        self.painter = QPainter()
        # 设置起点和终点，并设置标志位以控制打点
        self.vertexes = []
        # self.vertexes = [(2, 2), (5, 1), (11, 3), (11, 8), (5, 5), (2, 7)]
        # self.vertexes = [(x*50, y*50) for x, y in self.vertexes]
        # 裁剪窗口的左上角和右下角两点用以确定矩形
        self.clipWindowPoint1 = (0, 0)
        self.isDrawPoint1 = False
        self.clipWindowPoint3 = (0, 0)
        self.isDrawPoint3 = False

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

    def drawRectangle(self):
        clipWindowPoint2 = (self.clipWindowPoint3[0], self.clipWindowPoint1[1])
        clipWindowPoint4 = (self.clipWindowPoint1[0], self.clipWindowPoint3[1])
        print(clipWindowPoint2, clipWindowPoint4)
        self.BresenhamDrawLine(self.clipWindowPoint1[0], self.clipWindowPoint1[1],
                               clipWindowPoint2[0], clipWindowPoint2[1])
        self.BresenhamDrawLine(clipWindowPoint2[0], clipWindowPoint2[1],
                               self.clipWindowPoint3[0], self.clipWindowPoint3[1])
        self.BresenhamDrawLine(self.clipWindowPoint3[0], self.clipWindowPoint3[1],
                               clipWindowPoint4[0], clipWindowPoint4[1])
        self.BresenhamDrawLine(clipWindowPoint4[0], clipWindowPoint4[1],
                               self.clipWindowPoint1[0], self.clipWindowPoint1[1])

    def joinVertexes(self):
        if len(self.vertexes) < 3:
            return
        else:
            # 依次连接各点
            for i in range(len(self.vertexes) - 1):
                self.BresenhamDrawLine(self.vertexes[i][0], self.vertexes[i][1], self.vertexes[i + 1][0],
                                       self.vertexes[i + 1][1])
            # 连接第一个点和最后一个点
            self.BresenhamDrawLine(self.vertexes[0][0], self.vertexes[0][1], self.vertexes[-1][0], self.vertexes[-1][1])

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if event.buttons() == QtCore.Qt.LeftButton:  # 左键按下
            self.vertexes.append((x, y))
            self.paintPoint(x, y)
        elif event.buttons() == QtCore.Qt.RightButton:  # 如果点击的是右键，则通过两点绘制正则矩形作为裁剪窗口
            if not self.isDrawPoint1:
                self.clipWindowPoint1 = (x, y)
                self.isDrawPoint1 = True
                self.paintPoint(x, y)
            elif not self.isDrawPoint3:
                self.clipWindowPoint3 = (x, y)
                self.isDrawPoint3 = True
                self.paintPoint(x, y)
            else:
                self.drawRectangle()
        else:   # 点击其他键（一般是中键）来绘制多边形
            self.joinVertexes()

    def mouseDoubleClickEvent(self, event):
        self.board.fill(Qt.white)
        self.update()
        # 回到初始状态
        self.vertexes.clear()

    def BresenhamDrawLine(self, x0, y0, x1, y1):
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
    polygon_pyqt = PolygonClip()
    polygon_pyqt.show()
    app.exec_()
