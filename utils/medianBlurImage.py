import cv2
import utils.imageProcess
from PIL import Image
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap

class MedianBlurImage(utils.imageProcess.ImageProcess):
    sendImagesToWidget = pyqtSignal(QPixmap, int)
    def __init__(self, parent=None):
        super(MedianBlurImage, self).__init__(parent)
       

    def process(self, input_image_path, output_image_path):
        # 加载图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        h, w = raw_image.shape[:2]
        send_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)   # 为了显示
        if raw_image is None:
            print("无法加载图像，请检查路径！")
            return
       # 添加椒盐噪声
        noisy_img = self.add_salt_and_pepper_noise(raw_image, amount=0.05)

        # OpenCV 的中值滤波
        opencv_filtered_img = cv2.medianBlur(noisy_img, ksize=3)

        noisy_img = cv2.cvtColor(noisy_img, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFramesToUI(send_image, 0)
        self.sendFramesToUI(noisy_img, 1)
        # 转为灰度图像
        opencv_filtered_img = cv2.cvtColor(opencv_filtered_img, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFramesToUI(opencv_filtered_img, 2)
        self._save_single_frame(opencv_filtered_img, self._save_path)

    def sendFramesToUI(self, frame, index):
        rgb_image = np.array(frame)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendImagesToWidget.emit(pixmap, index)

    
    def add_salt_and_pepper_noise(self, image, amount=0.05):
        """
        给图像添加椒盐噪声
        :param image: 输入图像（灰度图像）
        :param amount: 噪声比例
        :return: 添加噪声后的图像
        """
        noisy_image = image.copy()
        num_salt = int(amount * image.size * 0.5)
        num_pepper = int(amount * image.size * 0.5)

        # 添加盐噪声
        for _ in range(num_salt):
            i = random.randint(0, image.shape[0] - 1)
            j = random.randint(0, image.shape[1] - 1)
            noisy_image[i, j] = 255

        # 添加椒噪声
        for _ in range(num_pepper):
            i = random.randint(0, image.shape[0] - 1)
            j = random.randint(0, image.shape[1] - 1)
            noisy_image[i, j] = 0

        return noisy_image


    def median_filter(self, image, kernel_size=3):
        """
        自己实现的中值滤波函数
        :param image: 输入图像（灰度图像）
        :param kernel_size: 滤波器大小（必须是奇数）
        :return: 滤波后的图像
        """
        pad_size = kernel_size // 2
        padded_image = np.pad(image, ((pad_size, pad_size), (pad_size, pad_size)), mode='constant', constant_values=0)
        filtered_image = np.zeros_like(image)

        for i in range(image.shape[0]):
            for j in range(image.shape[1]):
                # 提取局部窗口
                window = padded_image[i:i + kernel_size, j:j + kernel_size]
                # 计算中值
                filtered_image[i, j] = np.median(window)

        return filtered_image

    def self_process(self, input_image_path, output_image_path):
        # 读取图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        if raw_image is None:
            raise FileNotFoundError("输入图像文件未找到！")

        # 添加椒盐噪声
        noisy_img = self.add_salt_and_pepper_noise(raw_image, amount=0.05)

        # 自己实现的中值滤波
        filtered_img = self.median_filter(noisy_img, kernel_size=3)

        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
        self.sendFramesToUI(raw_image, 0)

        # 转换为 OpenCV 可显示的格式
        noisy_img = cv2.cvtColor(noisy_img, cv2.COLOR_BGR2RGB)
        self.sendFramesToUI(noisy_img, 1)

        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2RGB)
        self.sendFramesToUI(filtered_img, 2)

        self._save_single_frame(filtered_img, self._save_path)

    def grayscaleAllImage(self):
        for image_path in self._image_file:
            if self._func_select:
                self.self_process(image_path, self._output_path)
            else:
                self.process(image_path, self._output_path)

    def run(self):
        self._cur_image_index = 0
        self._image_file.clear()
        self._save_path = self._makeOutputFolder()      # 
        self.getAllFileName( self._input_path)
        self._image_file.sort(key=self.sort_by_number)
        self.grayscaleAllImage()
        self._cur_image_index -= 1      #实际数量
