import os
import shutil
import cv2
import re
import numpy as np
import imageio

from PyQt5.QtCore import QThread,  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap



class GetImageFromFile(QThread):
    # 信号
    sendRawImageToWidget = pyqtSignal(QPixmap)
    sendDetailImageToWidget = pyqtSignal(QPixmap)
    sendImageIndexToWidget = pyqtSignal(int, int)
    sendCameraMsgToWidget = pyqtSignal(int, int, int, int, str, str)

    def __init__(self, parent=None):
        super(GetImageFromFile, self).__init__(parent)
        self._input_path = ''
        self._output_path = ''
        self._save_path = '~/Downloads'
        self._image_file = []
        self._save_format = 'png'
        self._cur_image_index = 0
        
    # 设置输入文件的路径
    def setInputFilePath(self, path):
        self._input_path = path
        print('Image input path=', self._input_path)

    # 设置输出文件的路径
    def setOutputPath(self, path):
        self._output_path = path
        print('Image output path=', self._output_path)

    # 设置要修改的宽高
    def setWidthHeight(self, w, h):
        self._desire_image_size =  (w, h)

    def setSaveFormat(self, save_format):
        self._save_format = save_format

    def _makeOutputFolder(self):
        path_parts = os.path.abspath(self._input_path).split(os.sep)
        # 去除上四级路径，获取剩余的路径
        remaining_path = os.sep.join(path_parts[-1:])
        save_path = os.path.join(self._output_path,"resize_result")
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
                file_path = os.path.join(root, file)  # 构建文件的绝对路径
                self._image_file.append(file_path)  # 将绝对路径添加到列表中

    def sendFrameToUI(self, frame, index):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV 默认使用BGR格式，转换成RGB格式
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


    # def resizeAndPadImage(self, input_image_path, output_image_path, size):
    #     desired_width, desired_height = size
    #     # 加载图像
    #     image = cv2.imread(input_image_path)
    #     self.sendFrameToUI(image, 1)
    #     original_height, original_width = image.shape[:2]

    #     # 计算缩放比例
    #     scale_x = desired_width / original_width
    #     scale_y = desired_height / original_height
    #     scale = min(scale_x, scale_y)
    #     # 根据比例因子计算放大后的尺寸
    #     new_width = int(original_width*scale)
    #     new_height = int(original_height*scale)
    #     # # 使用LapSRN x4模型
    #     # resized_image = upscale(img=image, alg_name='lapsrn', scale=2)
    #     # 缩放图像
    #     resized_image = cv2.resize(image, None, fx=scale, fy=scale)
    #     # 使用双线性插值方法进行放大
    #     # resized_image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_LINEAR)

    #     # 创建一个新的画布，填充空白区域
    #     padded_image = 255 * np.zeros((desired_height, desired_width, 3), dtype=np.uint8)
    #     pad_top = (desired_height - resized_image.shape[0]) // 2
    #     pad_left = (desired_width - resized_image.shape[1]) // 2
    #     padded_image[pad_top:pad_top+resized_image.shape[0], pad_left:pad_left+resized_image.shape[1]] = resized_image
    #     # 对填充后的图像进行增强（直方图均衡化）
    #     # gray_image = cv2.cvtColor(padded_image, cv2.COLOR_BGR2GRAY)
    #     # enhanced_image = cv2.equalizeHist(gray_image)
    #     # enhanced_image = cv2.cvtColor(enhanced_image, cv2.COLOR_GRAY2BGR)
    #     self.sendFrameToUI(padded_image, 2)
    #     # # 从绝对路径中提取文件名
    #     # filename = os.path.basename(input_image_path)
    #     # outpu_file_path = os.path.join(output_image_path, filename)  # 构建文件的绝对路径
    #     # # 保存输出图像
    #     # cv2.imwrite(outpu_file_path, padded_image)
    #     self._save_single_frame(padded_image, self._save_path)
    def resizeAndPadImage(self, input_image_path, output_image_path, size):
        """
        缩放并填充图片到目标尺寸，不使用PIL等高级库。
        
        Args:
            input_image_path (str): 输入图片路径。
            output_image_path (str): 输出图片路径。
            size (tuple): 目标尺寸 (width, height)。
        """
        # 读取图片为numpy数组
        image = imageio.imread(input_image_path)  # (H, W, C)

        # 提取目标宽高
        target_width, target_height = size

        # 原图片宽高
        original_height, original_width, _ = image.shape

        # 计算缩放比例，保持宽高比例一致
        scale_w = target_width / original_width
        scale_h = target_height / original_height
        scale = min(scale_w, scale_h)

        # 缩放后的宽高
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        # print(f"缩放比例: {scale}, 新尺寸: {new_width}x{new_height}")

        # 缩放图片 (双线性插值)
        resized_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
        for i in range(new_height):
            for j in range(new_width):
                src_x = j / scale
                src_y = i / scale
                x0, y0 = int(src_x), int(src_y)
                x1, y1 = min(x0 + 1, original_width - 1), min(y0 + 1, original_height - 1)

                dx, dy = src_x - x0, src_y - y0
                resized_image[i, j] = (
                    (1 - dx) * (1 - dy) * image[y0, x0]
                    + dx * (1 - dy) * image[y0, x1]
                    + (1 - dx) * dy * image[y1, x0]
                    + dx * dy * image[y1, x1]
                )

        # 创建目标画布
        result_image = np.zeros((target_height, target_width, 3), dtype=np.uint8)

        # 计算粘贴的起始位置
        top = (target_height - new_height) // 2
        left = (target_width - new_width) // 2

        # 将缩放图片粘贴到画布中央
        result_image[top:top+new_height, left:left+new_width] = resized_image
        r_array = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(r_array, 1)
        result_image = cv2.cvtColor(result_image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(result_image, 2)
        self._save_single_frame(result_image, self._save_path)

    def resizeAllImage(self):
        print(self._desire_image_size)
        for image_path in self._image_file:
            self.resizeAndPadImage(image_path, self._output_path, self._desire_image_size)
        # self._cur_image_index = len(self._image_file) - 1
            
    # 自定义排序函数，根据文件名中的数字进行排序
    def sort_by_number(self, file_name):
        parts = re.split(r'(\d+)', file_name)
        return [int(part) if part.isdigit() else part for part in parts]
    
    def run(self):
        self._save_path = self._makeOutputFolder()
        self.getAllFileName( self._input_path)
        self._image_file.sort(key=self.sort_by_number)
        self.resizeAllImage()

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
