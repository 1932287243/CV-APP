import os
import shutil
import cv2
import re
import numpy as np

from PyQt5.QtCore import QThread,  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap



class FormatConversion(QThread):
    # 信号
    sendRawImageToWidget = pyqtSignal(QPixmap)
    sendImageIndexToWidget = pyqtSignal(int, int)
    sendCameraMsgToWidget = pyqtSignal(int, int, int, int, str, str)

    def __init__(self, parent=None):
        super(FormatConversion, self).__init__(parent)
        self._input_path = ''
        self._output_path = '~/Downloads'
        self._image_file = []
        self._target_format = ''
        self._cur_format = ''
        self._cur_image_index = 0
        self._height = 0
        self._width = 0
        
    # 设置输入文件的路径
    def setInputFilePath(self, path):
        self._input_path = path

    # 设置输出文件的路径
    def setOutputPath(self, path):
        self._output_path = path

    # 设置要修改的宽高
    def setWidthHeight(self, w, h):
        self._height = h
        self._width = w

    def setSaveFormat(self, cur_format, save_format):
        self._target_format = save_format
        self._cur_format = cur_format

    # 获取输入路径下的所有文件
    def getAllFileName(self, folder_path):
        self._image_file.clear()
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)  # 构建文件的绝对路径
                self._image_file.append(file_path)  # 将绝对路径添加到列表中

    def _makeOutputFolder(self):
        path_parts = os.path.abspath(self._input_path).split(os.sep)
        # 去除上四级路径，获取剩余的路径
        remaining_path = os.sep.join(path_parts[-1:])
        save_path = os.path.join(self._output_path,"convert_result")
        save_path = os.path.join(save_path, remaining_path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        else:
            shutil.rmtree(save_path)
            os.makedirs(save_path)
        return save_path
    
    def sendFrameToUI(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV 默认使用BGR格式，转换成RGB格式
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendRawImageToWidget.emit(pixmap)

    def _save_single_frame(self,frame, path):
        if self._target_format == 'png':
            filename = os.path.join(path, f'{self._cur_image_index:010d}.png')
            cv2.imwrite(filename, frame)
        elif self._target_format == 'jpg':
            filename = os.path.join(path, f'{self._cur_image_index:010d}.jpg')
            cv2.imwrite(filename, frame)
        elif self._target_format == 'yuv420p' or self._target_format == 'yuv420sp':
            filename = os.path.join(path, f'{self._cur_image_index:010d}.yuv')
            # 将 YUV 数据写入文件
            with open(filename, 'wb') as f:
                f.write(frame.tobytes())

        self._cur_image_index += 1
        self.sendImageIndexToWidget.emit(self._cur_image_index, len(self._image_file))

    def rgb2yuv42p(self, filename):
        img = cv2.imread(filename)
        self.sendFrameToUI(img)
        yuv_image_raw = cv2.cvtColor(img, cv2.COLOR_BGR2YUV_I420)#YUV420P
        self._save_single_frame(yuv_image_raw, self._save_path)

    def yuv420p2rgb(self, filename):
        img = np.fromfile(filename, dtype=np.uint8)
        yuv420p = img.reshape(int(self._height*1.5), self._width)
        target_img = cv2.cvtColor(yuv420p, cv2.COLOR_YUV2BGR_I420)
        self.sendFrameToUI(target_img)
        self._save_single_frame(target_img, self._save_path)
     
    def rgb2yuv420sp(self, filename):
        # 读取 RGB 图像
        rgb_image = cv2.imread(filename)
        self.sendFrameToUI(rgb_image)
        height,width = rgb_image.shape[0:2]
        # 将 RGB 转换为 YUV420 格式
        yuv_image = cv2.cvtColor(rgb_image, cv2.COLOR_BGR2YUV_I420)
        # 获取 Y、U、V 分量
        y_channel = yuv_image[:height]
        u_channel = yuv_image[height:height+int(0.25*height)]
        v_channel = yuv_image[-int(0.25*height):]
        # 重排 U 和 V 分量以生成 NV12 格式
        uv_combined = np.empty((u_channel.shape[0]*2, u_channel.shape[1]), dtype=u_channel.dtype)
        uv_combined[0::1,0::2] = u_channel.reshape(uv_combined[0::1,0::2].shape[0],-1)
        uv_combined[0::1,1::2] = v_channel.reshape(uv_combined[0::1,0::2].shape[0],-1)
        # 创建 NV12 图像
        nv12_image = np.vstack([y_channel, uv_combined])
        # 保存 NV12 图像
        self._save_single_frame(nv12_image, self._save_path)
    
    def yuv420sp2rgb(self, filename):
        yuv_data = np.fromfile(filename, dtype=np.uint8)
        yuv420sp = yuv_data.reshape(int(self._height*1.5), self._width)
        rgb_image = cv2.cvtColor(yuv420sp, cv2.COLOR_YUV420sp2RGB)
        self.sendFrameToUI(rgb_image)
        # 保存 NV12 图像
        self._save_single_frame(rgb_image, self._save_path)
        
    def convertImage(self):
        print("_cur_format=",self._cur_format)
        print("_target_format=",self._target_format)
        for image_path in self._image_file:
            if self._cur_format == 'png' or self._cur_format == 'jpg':
                if self._target_format == 'yuv420p':
                    self.rgb2yuv42p(image_path)
                if self._target_format == 'yuv420sp':
                    self.rgb2yuv420sp(image_path)
            if self._cur_format == 'yuv420p':
                if self._target_format == 'png' or self._target_format == 'jpg':
                    self.yuv420p2rgb(image_path)
            if self._cur_format == 'yuv420sp':
                if self._target_format == 'png' or self._target_format == 'jpg':
                    self.yuv420sp2rgb(image_path)
    
    # 自定义排序函数，根据文件名中的数字进行排序
    def sort_by_number(self, file_name):
        parts = re.split(r'(\d+)', file_name)
        return [int(part) if part.isdigit() else part for part in parts]

    def run(self):
        self._cur_image_index = 0
        self.getAllFileName(self._input_path)
        # 按文件名排序
        self._image_file.sort(key=self.sort_by_number)
        self._save_path = self._makeOutputFolder()
        self.convertImage()

     # 上一张图片
    def changeImageBackward(self, tab_index, list_index):
        if tab_index == 2 and list_index == 1:
            self._cur_image_index += 1
            image_index_path = os.path.join(self._output_path, f'{self._cur_image_index}.{self._save_format}')
            if self._cur_image_index < len(self._image_file):
                pixmap = QPixmap(image_index_path)
                self.sendRawImageToWidget.emit(pixmap)
            else:
                image_index_path = os.path.join(self._output_path, f'{0}.{self._save_format}')
                pixmap = QPixmap(image_index_path)
                self.sendRawImageToWidget.emit(pixmap)
                self._cur_image_index = 0
            self.sendImageIndexToWidget.emit(self._cur_image_index+1, len(self._image_file))
            
    # 下一张图片
    def changeImageForward(self, tab_index, list_index):
        if tab_index == 2 and list_index == 1:
            self._cur_image_index -= 1
            image_index_path = os.path.join(self._output_path, f'{self._cur_image_index}.{self._save_format}')
            if self._cur_image_index < 0:
                image_index_path = os.path.join(self._output_path, f'{len(self._image_file) - 1}.{self._save_format}')
                pixmap = QPixmap(image_index_path)
                self.sendRawImageToWidget.emit(pixmap)
                self._cur_image_index = len(self._image_file) - 1
            else:
                pixmap = QPixmap(image_index_path)
                self.sendRawImageToWidget.emit(pixmap)
            self.sendImageIndexToWidget.emit(self._cur_image_index+1, len(self._image_file))
