import sys

from PyQt5 import QtCore
from PyQt5.QtWidgets import (QApplication, QWidget)
from PyQt5.QtGui import (QPainter, QPen, QPixmap)
from PyQt5.QtCore import Qt


class PolygonClip(QWidget):

    def __init__(self):
        super(PolygonClip, self).__init__()
        self.resize(800, 600)
        self.board = QPixmap(800, 600)
        self.board.fill(Qt.white)
        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)
        self.painter = QPainter()
        # 设置起点和终点，并设置标志位以控制打点
        self.vertexes = []
        self.polygon_drawn = False
        # 裁剪窗口的左上角和右下角两点用以确定矩形
        self.clipWindowPoint1 = (0, 0)
        self.isDrawPoint1 = False
        self.clipWindowPoint3 = (0, 0)
        self.isDrawPoint3 = False

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

    def draw_rectangle(self):
        clipWindowPoint2 = (self.clipWindowPoint3[0], self.clipWindowPoint1[1])
        clipWindowPoint4 = (self.clipWindowPoint1[0], self.clipWindowPoint3[1])
        self.bresenham_drawline(self.clipWindowPoint1[0], self.clipWindowPoint1[1],
                                clipWindowPoint2[0], clipWindowPoint2[1], Qt.blue)
        self.bresenham_drawline(clipWindowPoint2[0], clipWindowPoint2[1],
                                self.clipWindowPoint3[0], self.clipWindowPoint3[1], Qt.blue)
        self.bresenham_drawline(self.clipWindowPoint3[0], self.clipWindowPoint3[1],
                                clipWindowPoint4[0], clipWindowPoint4[1], Qt.blue)
        self.bresenham_drawline(clipWindowPoint4[0], clipWindowPoint4[1],
                                self.clipWindowPoint1[0], self.clipWindowPoint1[1], Qt.blue)

    def join_vertexes(self, vertexes, color):
        if len(vertexes) < 3:
            return
        else:
            # 依次连接各点
            for i in range(len(vertexes) - 1):
                self.bresenham_drawline(vertexes[i][0], vertexes[i][1], vertexes[i + 1][0],
                                        vertexes[i + 1][1], color)
            # 连接第一个点和最后一个点
            self.bresenham_drawline(vertexes[0][0], vertexes[0][1], vertexes[-1][0],
                                    vertexes[-1][1], color)

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if event.buttons() == QtCore.Qt.LeftButton and not self.polygon_drawn:  # 左键按下
            self.vertexes.append((x, y))
            self.paintPoint(x, y, Qt.black)
        elif event.buttons() == QtCore.Qt.RightButton:  # 如果点击的是右键，则通过两点绘制正则矩形作为裁剪窗口
            if not self.isDrawPoint1:
                self.clipWindowPoint1 = (x, y)
                self.isDrawPoint1 = True
                self.paintPoint(x, y, Qt.blue)
            elif not self.isDrawPoint3:
                self.clipWindowPoint3 = (x, y)
                self.isDrawPoint3 = True
                self.paintPoint(x, y, Qt.blue)
            else:
                self.draw_rectangle()
                self.isDrawPoint1 = False
                self.isDrawPoint3 = False
        else:  # 点击其他键（一般是中键）来绘制多边形
            self.join_vertexes(self.vertexes, Qt.black)
            self.polygon_drawn = True

    def mouseDoubleClickEvent(self, event):
        if event.buttons() == QtCore.Qt.RightButton:
            self.board.fill(Qt.white)
            self.update()
            # 回到初始状态
            self.vertexes.clear()
            self.polygon_drawn = False
            self.clipWindowPoint1 = (0, 0)
            self.isDrawPoint1 = False
            self.clipWindowPoint3 = (0, 0)
            self.isDrawPoint3 = False
        elif event.buttons() == QtCore.Qt.LeftButton:
            self.sh_clip()
        else:
            pass

    # 求矩形的横边与多边形某条边的交点
    def calc_intersection_length(self, x0, y0, x1, y1, y_length):
        # 多边形的边是平行于x轴的
        if y0 == y1:
            return
        x = x0 + (y_length - y0) * (x1 - x0) / (y1 - y0)
        return x, y_length

    # 求矩形的竖边与多边形某条边的交点
    def calc_intersection_width(self, x0, y0, x1, y1, x_width):
        # 多边形的边是平行于y轴的
        if x0 == x1:
            return
        y = y0 + (x_width - x0) * (y1 - y0) / (x1 - x0)
        return x_width, y

    def clip(self, x0, y0, x1, y1):
        retained_points = []
        for i in range(len(self.vertexes)):
            k = (i + 1) % (len(self.vertexes))
            sx = self.vertexes[i][0]
            sy = self.vertexes[i][1]
            px = self.vertexes[k][0]
            py = self.vertexes[k][1]

            # 通过向量叉积分别判断点s, p是否在边界内侧
            s_in = (x1 - x0) * (sy - y0) - (y1 - y0) * (sx - x0)
            p_in = (x1 - x0) * (py - y0) - (y1 - y0) * (px - x0)
            # 四种情况分别处理
            # 1. 都在内侧，保留点p
            if s_in >= 0 and p_in >= 0:
                retained_points.append((px, py))
            # 2. s在外侧，p在内侧，保留p和交点
            elif s_in < 0 and p_in >= 0:
                if x0 == x1:  # 竖边
                    retained_points.append(self.calc_intersection_width(sx, sy, px, py, x0))
                else:  # 横边
                    retained_points.append(self.calc_intersection_length(sx, sy, px, py, y0))
                retained_points.append((px, py))
            # 3. s在内侧，p在外侧，保留交点
            elif s_in >= 0 and p_in < 0:
                if x0 == x1:  # 竖边
                    retained_points.append(self.calc_intersection_width(sx, sy, px, py, x0))
                else:  # 横边
                    retained_points.append(self.calc_intersection_length(sx, sy, px, py, y0))
            # 4. 都在外侧，不保留
            else:
                pass
        # 本次保留的多边形作为下一次裁剪的裁剪对象
        self.vertexes = retained_points

    def sh_clip(self):
        # 按照正则矩形的下边开始逆时针依次进行裁剪
        self.clip(self.clipWindowPoint1[0], self.clipWindowPoint1[1],
                  self.clipWindowPoint3[0], self.clipWindowPoint1[1])
        self.clip(self.clipWindowPoint3[0], self.clipWindowPoint1[1],
                  self.clipWindowPoint3[0], self.clipWindowPoint3[1])
        self.clip(self.clipWindowPoint3[0], self.clipWindowPoint3[1],
                  self.clipWindowPoint1[0], self.clipWindowPoint3[1])
        self.clip(self.clipWindowPoint1[0], self.clipWindowPoint3[1],
                  self.clipWindowPoint1[0], self.clipWindowPoint1[1])
        self.vertexes = [(int(x), int(y)) for x, y in self.vertexes]
        self.join_vertexes(self.vertexes, Qt.red)

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
    polygon_pyqt = PolygonClip()
    polygon_pyqt.show()
    app.exec_()
