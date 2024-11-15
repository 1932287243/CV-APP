import os
import shutil
import numpy as np
import re
import cv2

from PyQt5.QtCore import QThread,  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap

class ImageProcess(QThread):
    # 信号
    sendRawImageToWidget = pyqtSignal(QPixmap)
    sendDetailImageToWidget = pyqtSignal(QPixmap)
    sendImageIndexToWidget = pyqtSignal(int, int)
    sendCameraMsgToWidget = pyqtSignal(int, int, int, int, str, str)

    def __init__(self, parent=None):
        super(ImageProcess, self).__init__(parent)
        self._input_path = ''   # 需要处理的文件
        self._output_path = ''  # 处理后存放的文件
        self._save_path = '~/Downloads'
        self._image_file = []   # 获取需要处理目录下所有的图片文件
        self._save_format = 'jpg'
        self._cur_image_index = 0
        self._func_select = 0
        
    # 设置输入文件的路径
    def setInputPath(self, path):
        self._input_path = path
        print('Image input path=', self._input_path)

    # 设置输出文件的路径
    def setOutputPath(self, path):
        self._output_path = path
        print('Image output path=', self._output_path)
    
    # 创建保存的文件夹
    def _makeOutputFolder(self):
        path_parts = os.path.abspath(self._input_path).split(os.sep)
        # 去除上四级路径，获取剩余的路径
        remaining_path = os.sep.join(path_parts[-1:])
        save_path = os.path.join(self._output_path,"process_result")
        save_path = os.path.join(save_path, remaining_path)
        print("save_path:",save_path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        else:
            shutil.rmtree(save_path)
            os.makedirs(save_path)
        return save_path
    
    # 获取输入路径下的所有文件
    def getAllFileName(self, folder_path):
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                # 检查文件扩展名是否为 .png 或 .jpg
                if file.lower().endswith(('.png', '.jpg')):
                    file_path = os.path.join(root, file)  # 构建文件的绝对路径
                    self._image_file.append(file_path)  # 将绝对路径添加到列表中

    def sendFrameToUI(self, frame, index):
        # rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV 默认使用BGR格式，转换成RGB格式
        rgb_image = np.array(frame)
        # rgb_image = frame
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        if index == 1:
            self.sendRawImageToWidget.emit(pixmap)
        if index == 2:
            self.sendDetailImageToWidget.emit(pixmap)

    def _save_single_frame(self,frame, path):
        if self._save_format == 'png':
            filename = os.path.join(path, f'{self._cur_image_index}.png')
            cv2.imwrite(filename, frame)
        elif self._save_format == 'jpg':
            filename = os.path.join(path, f'{self._cur_image_index}.jpg')
            cv2.imwrite(filename, frame)
        elif self._save_format == 'yuv':
            filename = os.path.join(path, f'{self._cur_image_index}.yuv')
            yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
            # 将 YUV 数据写入文件
            with open(filename, 'wb') as f:
                f.write(yuv_frame.tobytes())

        self._cur_image_index += 1
        self.sendImageIndexToWidget.emit(self._cur_image_index, len(self._image_file))

    # 自定义排序函数，根据文件名中的数字进行排序
    def sort_by_number(self, file_name):
        parts = re.split(r'(\d+)', file_name)
        return [int(part) if part.isdigit() else part for part in parts]
    
     # 上一张图片
    def changeImageForward(self):
        self._cur_image_index += 1
        image_index_path_p = os.path.join(self._save_path, f'{self._cur_image_index}.{self._save_format}')
        image_index_path_r = os.path.join(self._input_path, f'{self._cur_image_index}.{self._save_format}')
        if self._cur_image_index < len(self._image_file):
            pixmap_p = QPixmap(image_index_path_p)
            self.sendDetailImageToWidget.emit(pixmap_p)
            pixmap_r = QPixmap(image_index_path_r)
            self.sendRawImageToWidget.emit(pixmap_r)
        else:
            image_index_path_p = os.path.join(self._save_path, f'{0}.{self._save_format}')
            image_index_path_r = os.path.join(self._input_path, f'{0}.{self._save_format}')
            pixmap_p = QPixmap(image_index_path_p)
            self.sendDetailImageToWidget.emit(pixmap_p)
            pixmap_r = QPixmap(image_index_path_r)
            self.sendRawImageToWidget.emit(pixmap_r)
            self._cur_image_index = 0
        self.sendImageIndexToWidget.emit(self._cur_image_index+1, len(self._image_file))
            
    # 下一张图片
    def changeImageBackward(self):
        self._cur_image_index -= 1
        image_index_path_p = os.path.join(self._save_path, f'{self._cur_image_index}.{self._save_format}')
        image_index_path_r = os.path.join(self._input_path, f'{self._cur_image_index}.{self._save_format}')
        if self._cur_image_index < 0:
            image_index_path_p = os.path.join(self._save_path, f'{len(self._image_file) - 1}.{self._save_format}')
            pixmap_p = QPixmap(image_index_path_p)
            self.sendDetailImageToWidget.emit(pixmap_p)
            image_index_path_r = os.path.join(self._input_path, f'{len(self._image_file) - 1}.{self._save_format}')
            pixmap_r = QPixmap(image_index_path_r)
            self.sendRawImageToWidget.emit(pixmap_r)
            self._cur_image_index = len(self._image_file)
        else:
            pixmap_p = QPixmap(image_index_path_p)
            self.sendDetailImageToWidget.emit(pixmap_p)
            pixmap_r = QPixmap(image_index_path_r)
            self.sendRawImageToWidget.emit(pixmap_r)
        self.sendImageIndexToWidget.emit(self._cur_image_index-1, len(self._image_file))
