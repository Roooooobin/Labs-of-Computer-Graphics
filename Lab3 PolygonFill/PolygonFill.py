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

class PolygonFill(QWidget):

    def __init__(self):
        super(PolygonFill, self).__init__()
        self.board = QPixmap(1000, 500)
        self.board.fill(Qt.white)
        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)
        self.painter = QPainter()
        # 设置起点和终点，并设置标志位以控制打点
        self.vertexes = []
        # self.vertexes = [(2, 2), (5, 1), (11, 3), (11, 8), (5, 5), (2, 7)]
        # self.vertexes = [(x*50, y*50) for x, y in self.vertexes]
        self.ET = []  # 类似于一个以扫描线y坐标为索引的哈希表
        self.AET = None

    def paintEvent(self, paintEvent):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, self.board)
        self.painter.end()

    def paintPoint(self, x, y):
        self.painter.begin(self.board)
        self.painter.setPen(QPen(Qt.blue, 6))
        self.painter.drawPoint(x, y)
        self.painter.end()
        self.update()

    # 涂色
    def fillPolygon(self, x, y):
        self.painter.begin(self.board)
        self.painter.setPen(QPen(Qt.blue, 6))
        self.painter.drawPoint(x, y)
        self.painter.end()
        self.update()

    def joinVertexes(self):
        if len(self.vertexes) < 3:
            return
        else:
            # 依次连接各点
            for i in range(len(self.vertexes)-1):
                self.BresenhamDrawLine(self.vertexes[i][0], self.vertexes[i][1], self.vertexes[i+1][0], self.vertexes[i+1][1])
            # 连接第一个点和最后一个点
            self.BresenhamDrawLine(self.vertexes[0][0], self.vertexes[0][1], self.vertexes[-1][0], self.vertexes[-1][1])

    def scanlineFill(self):
        maxY = max([t[1] for t in self.vertexes])  # 计算得出图形最高点的y坐标以确定扫描线范围
        # 初始ET和AET
        for i in range(maxY+1):
            edge = Edge()
            edge.next = None
            self.ET.append(edge)
        self.AET = Edge()
        self.AET.next = None
        size_vertexes = len(self.vertexes)
        # 建立边表ET
        for i in range(size_vertexes):
            # 取出当前点1前后相邻的共4个点，点1与点2的连线作为本次循环处理的边，另外两个点点0和点3用于计算奇点
            x0 = self.vertexes[(i-1+size_vertexes) % size_vertexes][0]
            x1 = self.vertexes[i][0]
            x2 = self.vertexes[(i+1) % size_vertexes][0]
            x3 = self.vertexes[(i+2) % size_vertexes][0]
            y0 = self.vertexes[(i-1+size_vertexes) % size_vertexes][1]
            y1 = self.vertexes[i][1]
            y2 = self.vertexes[(i+1) % size_vertexes][1]
            y3 = self.vertexes[(i+2) % size_vertexes][1]
            # 水平线直接跳过
            if y1 == y2:
                continue
            # 分别计算下端点y坐标、上端点y坐标、下端点x坐标和斜率倒数
            y_min = y1 if y1 < y2 else y2
            y_max = y2 if y1 < y2 else y1
            x = x1 if y1 < y2 else x2
            dx = (x1 - x2) / (y1 - y2)
            # 奇点特殊处理，若点2->1->0的y坐标单调递减则y1为奇点，若点1->2->3的y坐标单调递减则y2为奇点
            if ((y0 < y1) and (y1 < y2)) or ((y3 < y2) and (y2 < y1)):
                y_min += 1
                x += dx
            edge = Edge()
            edge.x = x
            edge.y_max = y_max
            edge.dx = dx
            edge.next = self.ET[y_min].next
            self.ET[y_min].next = edge
        # 扫描线从下往上开始扫描
        for i in range(0, maxY):
            while self.ET[i].next:
                eInsert = self.ET[i].next
                e = self.AET
                while e.next:
                    if eInsert.x > e.next.x:
                        e = e.next
                        continue
                    if eInsert.x == e.next.x and eInsert.dx > e.next.dx:
                        e = e.next
                        continue
                    break
                self.ET[i].next = eInsert.next
                eInsert.next = e.next
                e.next = eInsert

            # AET中的边两两配对并填色
            e = self.AET
            while e.next and e.next.next:
                for m in range(int(e.next.x), int(e.next.next.x)):
                    self.fillPolygon(m, i)
                e = e.next.next

            e = self.AET
            while e.next:
                if e.next.y_max == i:
                    eDelete = e.next
                    e.next = eDelete.next
                    eDelete.next = None
                    del eDelete
                else:
                    e = e.next
            # 更新AET，进入下一个循环
            e = self.AET
            while e.next:
                e.next.x += e.next.dx
                e = e.next

    def mousePressEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:  # 左键按下
            x = event.pos().x()
            y = event.pos().y()
            self.vertexes.append((x, y))
            self.paintPoint(x, y)
        else:   # 如果点击的不是左键，则连接各顶点构成多边形
            self.joinVertexes()
            self.scanlineFill()

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
    polygon_pyqt = PolygonFill()
    polygon_pyqt.show()
    app.exec_()
