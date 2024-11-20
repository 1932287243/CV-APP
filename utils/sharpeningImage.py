import cv2
import utils.imageProcess
from PIL import Image
import numpy as np
import matplotlib
matplotlib.use('Agg')  # 非交互式后端
import matplotlib.pyplot as plt
from PyQt5.QtCore import  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap

class SharpeningImage(utils.imageProcess.ImageProcess):
    sendImagesToWidget = pyqtSignal(QPixmap, int)
    def __init__(self, parent=None):
        super(SharpeningImage, self).__init__(parent)
        self.sharpening_mode = ""

    def process(self, input_image_path, output_image_path):
        # 加载图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        h, w = raw_image.shape[:2]
        send_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)   # 为了显示
        if raw_image is None:
            print("无法加载图像，请检查路径！")
            return

        # OpenCV 实现的锐化
        if self.sharpening_mode == "roberts":
            # result = self.opencv_sharpening(raw_image, operator="roberts")
            result = raw_image
        if self.sharpening_mode == "sobel":
            result = self.opencv_sharpening(raw_image, operator="sobel")
        if self.sharpening_mode == "laplace":
            result = self.opencv_sharpening(raw_image, operator="laplace")

        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFramesToUI(send_image, 0)
        self.sendFramesToUI(result, 1)
     
        self._save_single_frame(result, self._save_path)

    def sendFramesToUI(self, frame, index):
        rgb_image = np.array(frame)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendImagesToWidget.emit(pixmap, index)

    def apply_sharpening(self, image, operator="roberts"):
        """
        对图像进行锐化处理
        :param image: 输入灰度图像
        :param operator: 锐化算子，可选 "roberts", "sobel", "laplace"
        :return: 锐化后的图像
        """
        if operator == "roberts":
            kernel_x = np.array([[1, 0], [0, -1]])
            kernel_y = np.array([[0, 1], [-1, 0]])
        elif operator == "sobel":
            kernel_x = np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
            kernel_y = np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]])
        elif operator == "laplace":
            kernel_x = np.array([[0, 1, 0], [1, -4, 1], [0, 1, 0]])
            kernel_y = None  # Laplace 只需要单个卷积核
        else:
            raise ValueError("Unsupported operator. Choose 'roberts', 'sobel', or 'laplace'.")

        # 应用卷积
        if kernel_y is not None:
            gradient_x = cv2.filter2D(image, -1, kernel_x)
            gradient_y = cv2.filter2D(image, -1, kernel_y)
            sharpened_image = cv2.addWeighted(gradient_x, 0.5, gradient_y, 0.5, 0)
        else:
            sharpened_image = cv2.filter2D(image, -1, kernel_x)

        return sharpened_image


    def opencv_sharpening(self, image, operator="sobel"):
        """
        使用 OpenCV 实现图像锐化
        :param image: 输入灰度图像
        :param operator: 锐化算子，可选 "sobel", "laplace"
        :return: 锐化后的图像
        """
        if operator == "sobel":
            grad_x = cv2.Sobel(image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(image, cv2.CV_64F, 0, 1, ksize=3)
            sharpened_image = cv2.convertScaleAbs(grad_x) + cv2.convertScaleAbs(grad_y)
        elif operator == "laplace":
            laplace = cv2.Laplacian(image, cv2.CV_64F)
            sharpened_image = cv2.convertScaleAbs(laplace)
        else:
            raise ValueError("Unsupported operator in OpenCV sharpening. Choose 'sobel' or 'laplace'.")

        return sharpened_image

    def self_process(self, input_image_path, output_image_path):
        # 读取图像
        raw_image = cv2.imread(input_image_path, cv2.IMREAD_GRAYSCALE)
        if raw_image is None:
            raise FileNotFoundError("输入图像文件未找到！")

        # 应用锐化
        if self.sharpening_mode == "roberts":
            result = self.apply_sharpening(raw_image, operator="roberts")
        if self.sharpening_mode == "sobel":
            result = self.apply_sharpening(raw_image, operator="sobel")
        if self.sharpening_mode == "laplace":
            result = self.apply_sharpening(raw_image, operator="laplace")

        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
        self.sendFramesToUI(raw_image, 0)

        result = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
        self.sendFramesToUI(result, 1)

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
