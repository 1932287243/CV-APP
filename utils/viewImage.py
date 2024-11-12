import os
import cv2
# import numpy as np
import re
from PyQt5.QtCore import QThread,  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap



class ViewImage(QThread):
    # 信号
    sendRawImageToWidget = pyqtSignal(QPixmap)
    sendImageIndexToWidget = pyqtSignal(int, int)
    sendCameraMsgToWidget = pyqtSignal(int, int, int, int, str, str)

    def __init__(self, parent=None):
        super(ViewImage, self).__init__(parent)
        self._input_path = ''
        self._cur_image_index = 0
        self._image_file = []
    
    # 设置输入文件的路径
    def setInputFilePath(self, path):
        self._input_path = path

    # 获取输入路径下的所有文件
    def getAllFileName(self, folder_path):
        # 获取文件夹中文件的数量
        file_count = len([f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))])
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)  # 构建文件的绝对路径
                self._image_file.append(file_path)  # 将绝对路径添加到列表中
                img = cv2.imread(file_path)
                self.sendFrameToUI(img)
                self._cur_image_index += 1

                _, file_extension = os.path.splitext(file)
                self.sendImageIndexToWidget.emit(self._cur_image_index, file_count)
                self.sendCameraMsgToWidget.emit(0,0,img.shape[1], img.shape[0], file_extension, ' ')

    def sendFrameToUI(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV 默认使用BGR格式，转换成RGB格式
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendRawImageToWidget.emit(pixmap)
   
    # 自定义排序函数，根据文件名中的数字进行排序
    def sort_by_number(self, file_name):
        parts = re.split(r'(\d+)', file_name)
        return [int(part) if part.isdigit() else part for part in parts]

    def run(self):
        self._cur_image_index = 0
        self._image_file.clear()
        self.getAllFileName( self._input_path)
        # 按文件名排序
        self._image_file.sort(key=self.sort_by_number)

     # 上一张图片
    def changeImageBackward(self):
        self._cur_image_index += 1
        if self._cur_image_index < len(self._image_file):
            pixmap = QPixmap(self._image_file[self._cur_image_index])
            self.sendRawImageToWidget.emit(pixmap)
            _, file_extension = os.path.splitext(self._image_file[self._cur_image_index])
        else:
            pixmap = QPixmap(self._image_file[0])
            self.sendRawImageToWidget.emit(pixmap)
            self._cur_image_index = 0
            _, file_extension = os.path.splitext(self._image_file[0])
        self.sendCameraMsgToWidget.emit(0,0,pixmap.width(), pixmap.height(), file_extension, ' ')
        self.sendImageIndexToWidget.emit(self._cur_image_index+1, len(self._image_file))
            
    # 下一张图片
    def changeImageForward(self):
        self._cur_image_index -= 1
        if self._cur_image_index < 0:
            self._cur_image_index = len(self._image_file) - 1
            pixmap = QPixmap( self._image_file[ self._cur_image_index])
            self.sendRawImageToWidget.emit(pixmap)
            _, file_extension = os.path.splitext(self._image_file[self._cur_image_index])
        else:
            pixmap = QPixmap( self._image_file[self._cur_image_index])
            self.sendRawImageToWidget.emit(pixmap)
            _, file_extension = os.path.splitext(self._image_file[self._cur_image_index])
      
        self.sendCameraMsgToWidget.emit(0,0,pixmap.width(), pixmap.height(), file_extension, ' ')
        self.sendImageIndexToWidget.emit(self._cur_image_index+1, len(self._image_file))
