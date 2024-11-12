from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class ScrollTextWindow(QWidget):
    """ 滚动字幕 """
    def __init__(self, parent=None, Geometry=tuple()):
        super().__init__(parent)
        # 设置两段字符串之间留白的宽度
        self.spacing = 100
        # 滚动字幕字体选择
        self.font_style = QFont('Microsoft YaHei', 14, 400)
        self.max_len_text = 400
        # 设置刷新时间和移动距离
        self.timeStep = 20
        self.moveStep = 1
        """ 初始化界面 """
        # self.setFixedHeight(80)
        self.setGeometry(Geometry[0],Geometry[1],Geometry[2],Geometry[3])
        self.setAttribute(Qt.WA_StyledBackground)
        # self.setStyleSheet("background-color: red;")  # 设置背景颜色为浅灰色

        # 下面这部分只是初始化，显示字幕具体内容在setText决定
        # 初始化Text为空
        self.Text = ''
        # 实例化定时器
        self.timer_label = QTimer(self)
        self.TextCurrentIndex = 0
        # 设置字符串溢出标志位
        self.isTextAllOut = False
        self.isTextTooLong = 0

    def setText(self,Text):
        self.Text = Text
        # 加上下一句是放置更新字幕后之前的timer依旧存在，导致滚动越来越快，不信你可以删了试试
        self.timer_label.deleteLater()
        self.timer_label = QTimer(self)
        self.TextCurrentIndex = 0
        # 设置字符串溢出标志位
        self.isTextAllOut = False
        # 调整窗口宽度
        self.adjustWindowWidth()
        # 初始化定时器
        self.timer_label.setInterval(self.timeStep)
        self.timer_label.timeout.connect(self.updateIndex)
        # 只要有一个字符串宽度大于窗口宽度就开启滚动：
        if self.isTextTooLong:
            self.timer_label.start()

    def move_pose(self,object):
        x,y,w,h = object.x(), object.y(), object.width(), object.height()
        self.setGeometry(x, y, w, h)
        # self.move(x+w*0.02, y-h*0.6)  # 移动字幕条的位置，让他处于label框内
        self.max_len_text = w*0.96  # 让字幕显示在框里(略小)

    def getTextWidth(self):
        """ 计算文本的总宽度 """
        songFontMetrics = QFontMetrics(self.font_style)
        self.TextWidth = songFontMetrics.width(self.Text)

    def adjustWindowWidth(self):
        """ 根据字符串长度调整窗口宽度 """
        self.getTextWidth()
        maxWidth = self.TextWidth
        # 判断是否有字符串宽度超过设定的滚动阈值
        self.isTextTooLong = self.TextWidth > self.max_len_text
        # 设置窗口的宽度
        self.setFixedWidth(min(maxWidth, self.max_len_text))

    def updateIndex(self):
        """ 更新下标 """
        self.update()
        self.TextCurrentIndex += 1
        # 设置下标重置条件
        resetTextIndexCond = self.TextCurrentIndex * self.moveStep >= self.TextWidth + self.spacing * self.isTextAllOut
        # 只要条件满足就要重置下标并将字符串溢出置位，保证在字符串溢出后不会因为留出的空白而发生跳变
        if resetTextIndexCond:
            self.TextCurrentIndex = 0
            self.isTextAllOut = True

    def paintEvent(self, e):
        """ 绘制文本 """
        # super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.black)
        # 绘制格式
        painter.setFont(self.font_style)
        if self.isTextTooLong:
            # 实际上绘制了两段完整的字符串
            # 从负的横坐标开始绘制第一段字符串
            painter.drawText(self.spacing * self.isTextAllOut - self.moveStep *
                             self.TextCurrentIndex, 24, self.Text)
            # 绘制第二段字符串
            painter.drawText(self.TextWidth - self.moveStep * self.TextCurrentIndex +
                             self.spacing * (1 + self.isTextAllOut), 24, self.Text)
        else:
            painter.drawText(0, 24, self.Text)