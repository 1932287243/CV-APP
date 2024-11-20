import cv2
import utils.imageProcess
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap

class EqualizeHistImage(utils.imageProcess.ImageProcess):
    sendImagesToWidget = pyqtSignal(QPixmap, int)
    def __init__(self, parent=None):
        super(EqualizeHistImage, self).__init__(parent)

    def process(self, input_image_path, output_image_path):
        # 加载图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        h, w = raw_image.shape[:2]
        send_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)   # 为了显示
        if raw_image is None:
            print("无法加载图像，请检查路径！")
            return
        # 自己实现的直方图和均衡化
        title_raw = "Raw Image Histogram"
        original_hist_raw = self.calculate_histogram(raw_image)   # 获取直方图图像
        hist_image_raw = self.plot_histogram_to_image(original_hist_raw, title_raw)

        # equalized_img = self.histogram_equalization(raw_image)
        opencv_equalized_img = cv2.equalizeHist(raw_image)

        title_result = "Result Image Histogram"
        equalized_hist = self.calculate_histogram(opencv_equalized_img)
        equalized_hist_image = self.plot_histogram_to_image(equalized_hist, title_result)
        
        self.sendFramesToUI(hist_image_raw, 0)
        self.sendFramesToUI(equalized_hist_image, 1)
        self.sendFrameToUI(send_image, 1)
        # opencv_equalized_img = cv2.equalizeHist(raw_image)
        # 转为灰度图像
        opencv_equalized_img = cv2.cvtColor(opencv_equalized_img, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(opencv_equalized_img, 2)
        self._save_single_frame(opencv_equalized_img, self._save_path)

    def sendFramesToUI(self, frame, index):
        rgb_image = np.array(frame)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendImagesToWidget.emit(pixmap, index)

    def plot_histogram_to_image(self, hist, title):
        """
        绘制直方图并返回图像数据
        :param hist: 直方图数据
        :param title: 标题
        :return: 图像数据（NumPy 数组）
        """
        # 创建一个 Matplotlib Figure
        fig = plt.figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        # 绘制直方图
        ax.bar(range(256), hist, color='gray', width=1)
        ax.set_title(title)
        ax.set_xlabel("Pixel Intensity")
        ax.set_ylabel("Frequency")
        
        # 移除多余的空白区域
        plt.tight_layout()

        # 将图形保存到内存中的一个缓冲区
        fig.canvas.draw()
        buf = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        width, height = fig.canvas.get_width_height()
        img = buf.reshape((height, width, 3))

        # 关闭 Matplotlib 图形
        plt.close(fig)

        # 返回 OpenCV 格式的图像（RGB 转 BGR）
        return cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    def calculate_histogram(self, img):
        """
        计算灰度图像的直方图
        :param img: 输入灰度图像
        :return: 直方图
        """
        hist = np.zeros(256, dtype=int)
        h, w = img.shape
        for i in range(h):
            for j in range(w):
                hist[img[i, j]] += 1
        return hist


    def histogram_equalization(self, img):
        """
        实现灰度图像的直方图均衡化
        :param img: 输入灰度图像
        :return: 均衡化后的图像
        """
        hist = self.calculate_histogram(img)
        cdf = np.cumsum(hist)  # 累积分布函数
        cdf_normalized = cdf / cdf[-1]  # 归一化到 [0, 1]
        equalized_img = np.round(cdf_normalized[img] * 255).astype(np.uint8)  # 映射到 [0, 255]
        return equalized_img

    def self_process(self, input_image_path, output_image_path):
        # 读取图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        if raw_image is None:
            raise FileNotFoundError("输入图像文件未找到！")
        # 自己实现的直方图和均衡化
        title_raw = "Raw Image Histogram"
        original_hist_raw = self.calculate_histogram(raw_image)   # 获取直方图图像
        hist_image_raw = self.plot_histogram_to_image(original_hist_raw, title_raw)

        equalized_img = self.histogram_equalization(raw_image)

        title_result = "Result Image Histogram"
        equalized_hist = self.calculate_histogram(equalized_img)
        equalized_hist_image = self.plot_histogram_to_image(equalized_hist, title_result)
        
        self.sendFramesToUI(hist_image_raw, 0)
        self.sendFramesToUI(equalized_hist_image, 1)

        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(raw_image, 1)

        output_image = cv2.cvtColor(equalized_img, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(output_image, 2)
        self._save_single_frame(equalized_img, self._save_path)

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
