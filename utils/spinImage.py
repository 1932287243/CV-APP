import cv2
from PIL import Image
import numpy as np
import utils.imageProcess

class SpinImage(utils.imageProcess.ImageProcess):
    def __init__(self, parent=None):
        super(SpinImage, self).__init__(parent)


    def process(self, input_image_path, output_image_path):
        # 加载图像
        image = cv2.imread(input_image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(image, 1)
        
        if image is None:
            print("无法加载图像，请检查路径！")
            return

        # 旋转图片 90 度
        rotated_image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        rotated_image = cv2.cvtColor(rotated_image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(rotated_image, 2)
        self._save_single_frame(rotated_image, self._save_path)

    def self_process(self, input_image_path, output_image_path):
        """
        将图片顺时针旋转90度并保存为ppm格式（不依赖任何库）
        :param input_path: 输入图片路径，要求为ppm格式
        :param output_path: 输出图片路径
        """

        # 使用Pillow加载图片
        img = Image.open(input_image_path)
        # 将灰度图转换为 NumPy 数组
        img_array = np.array(img)
        
        width, height = img.size
        pixels = list(img.getdata())  # 获取像素数据
        pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]  # 转换为二维数组

        # 手动旋转图片 90 度
        rotated_pixels = []
        for col in range(width):
            rotated_row = []
            for row in reversed(range(height)):
                rotated_row.append(pixels[row][col])
            rotated_pixels.append(rotated_row)

        # 创建一个新图片对象
        rotated_img = Image.new(img.mode, (height, width))  # 宽高互换
        rotated_flattened = [pixel for row in rotated_pixels for pixel in row]  # 展平像素列表
        rotated_img.putdata(rotated_flattened)

        # 将灰度图转换为 NumPy 数组
        r_array = np.array(rotated_img)
        # img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(img_array, 1)

        # r_array = cv2.cvtColor(r_array, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(r_array, 2)

        self._save_single_frame(r_array, self._save_path)

    def spinAllImage(self):
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
        self.spinAllImage()
        self._cur_image_index -= 1      #实际数量
