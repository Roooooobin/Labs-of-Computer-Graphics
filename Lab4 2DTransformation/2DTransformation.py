import math
import sys
import numpy as np

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QWidget)
from PyQt5.QtGui import (QPainter, QPen, QPixmap)
from PyQt5.QtCore import Qt


class Edge:
    def __init__(self):
        self.x = None  # 与扫描线相交的点的x坐标
        self.dx = None  # 斜率的倒数
        self.y_max = None  # 上端点的y坐标
        self.next = None  # 指向下一条边


class Transformation(QWidget):

    def __init__(self):
        super(Transformation, self).__init__()
        self.resize(800, 600)
        self.board = QPixmap(800, 600)
        self.board.fill(Qt.white)
        # setMouseTracking设置为False，否则不按下鼠标时也会跟踪鼠标事件
        self.setMouseTracking(False)
        self.painter = QPainter()
        """
        圆形
        """
        # 设置起点和终点，并设置标志位以控制打点
        self.radius = 0
        self.center_x = 0
        self.center_y = 0
        self.center_flag = False
        self.xr = 0
        self.yr = 0
        """
        线段和多边形
        """
        # 设置起点和终点，并设置标志位以控制打点
        self.vertexes = []
        self.ET = []  # 类似于一个以扫描线y坐标为索引的哈希表
        self.AET = None
        """
        UI控件
        """
        self.inputTranslationX = QtWidgets.QLineEdit(self)
        self.inputTranslationX.setText("")
        self.inputTranslationX.setGeometry(QtCore.QRect(700, 150, 50, 30))
        self.inputTranslationX.setStyleSheet("border-radius:10px;\n"
                                             "background-color:#4C88F7;\n"
                                             "color:#FFF;")
        self.inputTranslationY = QtWidgets.QLineEdit(self)
        self.inputTranslationY.setText("")
        self.inputTranslationY.setGeometry(QtCore.QRect(700, 200, 50, 30))
        self.inputTranslationY.setStyleSheet("border-radius:10px;\n"
                                             "background-color:#4C88F7;\n"
                                             "color:#FFF;")
        self.translationButton = QtWidgets.QPushButton(self)
        self.translationButton.setGeometry(QtCore.QRect(755, 200, 40, 30))
        self.translationButton.setText("平移")
        self.translationButton.setStyleSheet("border-radius:10px;\n"
                                             "background-color:#4C88F7;\n"
                                             "color:#FFF;")
        self.translationButton.setObjectName("translationButton")
        self.translationButton.clicked.connect(self.translation)

        self.inputRotation = QtWidgets.QLineEdit(self)
        self.inputRotation.setText("")
        self.inputRotation.setGeometry(QtCore.QRect(700, 270, 50, 30))
        self.inputRotation.setStyleSheet("border-radius:10px;\n"
                                         "background-color:#4C88F7;\n"
                                         "color:#FFF;")
        self.rotationButton = QtWidgets.QPushButton(self)
        self.rotationButton.setGeometry(QtCore.QRect(755, 270, 40, 30))
        self.rotationButton.setText("旋转")
        self.rotationButton.setStyleSheet("border-radius:10px;\n"
                                          "background-color:#4C88F7;\n"
                                          "color:#FFF;")
        self.rotationButton.clicked.connect(self.rotation)

        self.inputScalingX = QtWidgets.QLineEdit(self)
        self.inputScalingX.setText("")
        self.inputScalingX.setGeometry(QtCore.QRect(700, 350, 50, 30))
        self.inputScalingX.setStyleSheet("border-radius:10px;\n"
                                         "background-color:#4C88F7;\n"
                                         "color:#FFF;")
        self.inputScalingY = QtWidgets.QLineEdit(self)
        self.inputScalingY.setText("")
        self.inputScalingY.setGeometry(QtCore.QRect(700, 400, 50, 30))
        self.inputScalingY.setStyleSheet("border-radius:10px;\n"
                                         "background-color:#4C88F7;\n"
                                         "color:#FFF;")
        self.scalingButton = QtWidgets.QPushButton(self)
        self.scalingButton.setGeometry(QtCore.QRect(755, 400, 40, 30))
        self.scalingButton.setText("缩放")
        self.scalingButton.setStyleSheet("border-radius:10px;\n"
                                         "background-color:#4C88F7;\n"
                                         "color:#FFF;")
        self.scalingButton.clicked.connect(self.scaling)

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

    # 支持线段两点连接以及多边形连接
    def joinVertexes(self):
        if len(self.vertexes) == 0:
            return
        # 依次连接各点
        for i in range(len(self.vertexes) - 1):
            self.BresenhamDrawLine(self.vertexes[i][0], self.vertexes[i][1], self.vertexes[i + 1][0],
                                   self.vertexes[i + 1][1])
        # 连接第一个点和最后一个点
        self.BresenhamDrawLine(self.vertexes[0][0], self.vertexes[0][1], self.vertexes[-1][0], self.vertexes[-1][1])

    def mousePressEvent(self, event):
        x = event.pos().x()
        y = event.pos().y()
        if event.buttons() == QtCore.Qt.LeftButton:  # 左键按下表示画的点是为了画出线段
            self.vertexes.append((x, y))
            self.paintPoint(x, y)
        elif event.buttons() == QtCore.Qt.RightButton:  # 右键按下画出圆形
            if not self.center_flag:
                self.center_x = x
                self.center_y = y
                self.center_flag = True
            else:
                self.xr = x
                self.yr = y
                self.radius = math.sqrt((self.xr - self.center_x) ** 2 + (self.yr - self.center_y) ** 2)
                self.midPointDrawCircle()
        else:  # 如果点击的不是左键或右键，则连接各顶点构成多边形或线段（一般使用中键MidButton）
            self.joinVertexes()

    def mouseDoubleClickEvent(self, event):
        self.board.fill(Qt.white)
        self.update()
        # 回到初始状态
        self.vertexes.clear()
        self.center_x = 0
        self.center_y = 0
        self.radius = 0
        self.center_flag = False
        self.xr = 0
        self.yr = 0

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

    # 平移
    def translation(self):
        offset_x = self.inputTranslationX.text()
        offset_x = float(offset_x) if offset_x else 0
        offset_y = self.inputTranslationY.text()
        offset_y = float(offset_y) if offset_y else 0
        # 图形是圆
        if self.center_flag:
            self.center_x = int(self.center_x + offset_x)
            self.center_y = int(self.center_y + offset_y)
            self.midPointDrawCircle()
            self.center_flag = False
        # 图形是线段或多边形
        else:
            self.vertexes = [(int(x + offset_x), int(y + offset_y)) for x, y in self.vertexes]
            self.joinVertexes()
        self.inputTranslationX.setText("")
        self.inputTranslationY.setText("")

    # 旋转
    def rotation(self):
        angle = float(self.inputRotation.text()) if self.inputRotation.text() else 0
        angle = angle / 180 * math.pi
        sin = math.sin(angle)
        cos = math.cos(angle)
        rotateMatrix = np.matrix([[cos, -sin], [sin, cos]])
        if self.center_flag:
            rotated_xy = (rotateMatrix * np.matrix((self.center_x, self.center_y)).T).T.tolist()[0]
            self.center_x = int(rotated_xy[0])
            self.center_y = int(rotated_xy[1])
            self.midPointDrawCircle()
            self.center_flag = False
        # 图形是线段或多边形
        else:
            self.vertexes = [(rotateMatrix * np.matrix(xy).T).T.tolist()[0] for xy in self.vertexes]
            self.vertexes = [(int(x), int(y)) for x, y in self.vertexes]
            self.joinVertexes()
        self.inputRotation.setText("")

    # 缩放
    def scaling(self):
        scale_x = self.inputScalingX.text()
        scale_x = float(scale_x) if scale_x else 0
        scale_y = self.inputScalingY.text()
        scale_y = float(scale_y) if scale_y else 0
        scaleMatrix = np.matrix([[scale_x, 0], [0, scale_y]])
        # 图形是圆
        if self.center_flag:
            if scale_x != scale_y:
                return
            scaled_xy = (scaleMatrix * np.matrix((self.center_x, self.center_y)).T).T.tolist()[0]
            self.center_x = int(scaled_xy[0])
            self.center_y = int(scaled_xy[1])
            self.radius *= scale_x
            self.midPointDrawCircle()
            self.center_flag = False
        # 图形是线段或多边形
        else:
            self.vertexes = [(scaleMatrix * np.matrix(xy).T).T.tolist()[0] for xy in self.vertexes]
            self.vertexes = [(int(x), int(y)) for x, y in self.vertexes]
            self.joinVertexes()
        self.inputScalingX.setText("")
        self.inputScalingY.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    transform_pyqt = Transformation()
    transform_pyqt.show()
    app.exec_()
