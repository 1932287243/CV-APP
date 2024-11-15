import cv2
import utils.imageProcess
from PIL import Image
import numpy as np

class GrayscaleImage(utils.imageProcess.ImageProcess):
    def __init__(self, parent=None):
        super(GrayscaleImage, self).__init__(parent)


    def process(self, input_image_path, output_image_path):
        # 加载图像
        image = cv2.imread(input_image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(image, 1)

        if image is None:
            print("无法加载图像，请检查路径！")
            return

        # 转为灰度图像
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        gray_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(gray_image, 2)
        self._save_single_frame(gray_image, self._save_path)

    def self_process(self, input_image_path, output_image_path):
        """
        将图片灰度化并保存
        :param input_path: 输入图片路径
        :param output_path: 输出灰度化图片路径
        """
        # 打开图片
        img = Image.open(input_image_path)

        # 将灰度图转换为 NumPy 数组
        img_array = np.array(img)

        # 获取图片的宽和高
        width, height = img.size

        # 转换为 RGB 模式（如果图片不是 RGB 模式）
        img = img.convert("RGB")

        # 创建空白的灰度图
        gray_img = Image.new("L", (width, height))

        # 遍历每个像素
        for x in range(width):
            for y in range(height):
                # 获取像素的 RGB 值
                r, g, b = img.getpixel((x, y))
                
                # 按照灰度公式计算灰度值
                gray = int(0.299 * r + 0.587 * g + 0.114 * b)
                
                # 设置灰度值到灰度图
                gray_img.putpixel((x, y), gray)
        # 将灰度图转换为 NumPy 数组
        gray_array = np.array(gray_img)
        # img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2RGB)
        self.sendFrameToUI(img_array, 1)
        gray_array = cv2.cvtColor(gray_array, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(gray_array, 2)
        self._save_single_frame(gray_array, self._save_path)

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
