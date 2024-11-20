import cv2
import utils.imageProcess
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap

class FilterImage(utils.imageProcess.ImageProcess):
    sendImagesToWidget = pyqtSignal(QPixmap, int)
    def __init__(self, parent=None):
        super(FilterImage, self).__init__(parent)
        # 设置滤波器参数
        self.filter_types = ["lowpass", "highpass"]
        self.filter_names = ["ideal", "butterworth", "gaussian"]
        self.d0 = 50  # 截止频率
        self.n = 2    # 巴特沃斯滤波器阶数

    def process(self, input_image_path, output_image_path):
        # 加载图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        h, w = raw_image.shape[:2]
        send_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)   # 为了显示
        if raw_image is None:
            print("无法加载图像，请检查路径！")
            return
         # OpenCV 实现的锐化
        sobel_opencv_result = self.opencv_sharpening(raw_image, operator="sobel")
        laplace_opencv_result = self.opencv_sharpening(raw_image, operator="laplace")

        sobel_opencv_result = cv2.cvtColor(sobel_opencv_result, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFramesToUI(sobel_opencv_result, 0)
        # self.sendFramesToUI(equalized_hist_image, 1)
        self.sendFrameToUI(send_image, 1)
        # opencv_equalized_img = cv2.equalizeHist(raw_image)
        # 转为灰度图像
        laplace_opencv_result = cv2.cvtColor(laplace_opencv_result, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(laplace_opencv_result, 2)
        self._save_single_frame(laplace_opencv_result, self._save_path)

    def sendFramesToUI(self, frame, index):
        rgb_image = np.array(frame)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendImagesToWidget.emit(pixmap, index)

    def apply_filter_in_frequency_domain(self, image, filter_type="lowpass", filter_name="ideal", d0=30, n=1):
        """
        在频域对图像进行低通或高通滤波。
        
        :param image: 输入灰度图像
        :param filter_type: 滤波器类型，"lowpass" 或 "highpass"
        :param filter_name: 滤波器名称，"ideal", "butterworth", "gaussian"
        :param d0: 截止频率或标准差
        :param n: 巴特沃斯滤波器的阶数
        :return: 频域滤波后的图像
        """
        # 图像尺寸
        rows, cols = image.shape
        crow, ccol = rows // 2, cols // 2

        # 图像进行傅里叶变换并中心化
        dft = np.fft.fft2(image)
        dft_shift = np.fft.fftshift(dft)

        # 创建滤波器
        u = np.arange(rows).reshape(-1, 1)  # 列向量
        v = np.arange(cols)                # 行向量
        d_uv = np.sqrt((u - crow) ** 2 + (v - ccol) ** 2)

        if filter_name == "ideal":
            if filter_type == "lowpass":
                filter_mask = np.where(d_uv <= d0, 1, 0)
            elif filter_type == "highpass":
                filter_mask = np.where(d_uv > d0, 1, 0)
        elif filter_name == "butterworth":
            if filter_type == "lowpass":
                filter_mask = 1 / (1 + (d_uv / d0) ** (2 * n))
            elif filter_type == "highpass":
                filter_mask = 1 / (1 + (d0 / d_uv) ** (2 * n))
        elif filter_name == "gaussian":
            if filter_type == "lowpass":
                filter_mask = np.exp(-(d_uv ** 2) / (2 * (d0 ** 2)))
            elif filter_type == "highpass":
                filter_mask = 1 - np.exp(-(d_uv ** 2) / (2 * (d0 ** 2)))
        else:
            raise ValueError("Unsupported filter name. Choose 'ideal', 'butterworth', or 'gaussian'.")

        # 应用滤波器
        filtered_dft = dft_shift * filter_mask

        # 傅里叶逆变换
        filtered_dft_shift = np.fft.ifftshift(filtered_dft)
        filtered_image = np.fft.ifft2(filtered_dft_shift)
        filtered_image = np.abs(filtered_image)

        return filtered_image, filter_mask

    def self_process(self, input_image_path, output_image_path):
        # 读取图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        if raw_image is None:
            raise FileNotFoundError("输入图像文件未找到！")

        filtered_image1, filter_mask1 = self.apply_filter_in_frequency_domain(raw_image, "lowpass", "ideal", self.d0, self.n)
        filtered_image2, filter_mask2 = self.apply_filter_in_frequency_domain(raw_image, "lowpass", "butterworth", self.d0, self.n)
        filtered_image3, filter_mask3 = self.apply_filter_in_frequency_domain(raw_image, "lowpass", "gaussian", self.d0, self.n)
        
        # filtered_image1, filter_mask1 = self.apply_filter_in_frequency_domain(raw_image, "highpass", "ideal", self.d0, self.n)
        # filtered_image2, filter_mask2 = self.apply_filter_in_frequency_domain(raw_image, "highpass", "butterworth", self.d0, self.n)
        # filtered_image3, filter_mask3 = self.apply_filter_in_frequency_domain(raw_image, "highpass", "gaussian", self.d0, self.n)

        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
        self.sendFramesToUI(raw_image, 0)

        # 转换为 OpenCV 可显示的格式
        filtered_image1 = cv2.normalize(filtered_image1, None, 0, 255, cv2.NORM_MINMAX)
        filtered_image1 = filtered_image1.astype(np.uint8)
        filtered_image1 = cv2.cvtColor(filtered_image1, cv2.COLOR_BGR2RGB)
        self.sendFramesToUI(filtered_image1, 1)

        filtered_image2 = cv2.normalize(filtered_image2, None, 0, 255, cv2.NORM_MINMAX)
        filtered_image2 = filtered_image2.astype(np.uint8)
        filtered_image2 = cv2.cvtColor(filtered_image2, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(filtered_image2, 1)

        filtered_image3 = cv2.normalize(filtered_image3, None, 0, 255, cv2.NORM_MINMAX)
        filtered_image3 = filtered_image3.astype(np.uint8)
        filtered_image3 = cv2.cvtColor(filtered_image3, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(filtered_image3, 2)
        self._save_single_frame(filtered_image3, self._save_path)

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
