import cv2
import utils.imageProcess
from PIL import Image
import numpy as np

class ColorConvertImage(utils.imageProcess.ImageProcess):
    def __init__(self, parent=None):
        super(ColorConvertImage, self).__init__(parent)


    def process(self, input_image_path, output_image_path):
        # 加载图像
        image = cv2.imread(input_image_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(image, 1)

        if image is None:
            print("无法加载图像，请检查路径！")
            return

        # 反色处理
        inverted_image = cv2.bitwise_not(image)
        inverted_image = cv2.cvtColor(inverted_image, cv2.COLOR_BGR2RGB)
        inverted_image = cv2.cvtColor(inverted_image, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(inverted_image, 2)
        self._save_single_frame(inverted_image, self._save_path)

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
        

         # 根据图片的通道情况进行反色
        if img_array.ndim == 3:  # RGB 或 RGBA 图像
            inverted_array = 255 - img_array[:, :, :3]  # 仅反转 RGB 通道
            if img_array.shape[2] == 4:  # 如果是 RGBA，保留透明度通道
                alpha_channel = img_array[:, :, 3:]
                inverted_array = np.concatenate((inverted_array, alpha_channel), axis=2)
        elif img_array.ndim == 2:  # 灰度图像
            inverted_array = 255 - img_array
        else:
            raise ValueError("Unsupported image format!")

        # 转换为图像并保存
        inverted_img = Image.fromarray(inverted_array.astype('uint8'))

        # 将图转换为 NumPy 数组
        inverted_img = np.array(inverted_img)
        # img_array = cv2.cvtColor(img_array, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(img_array, 1)
        # inverted_img = cv2.cvtColor(inverted_img, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(inverted_img, 2)
        self._save_single_frame(inverted_img, self._save_path)

    def colorConvertAllImage(self):
        for image_path in self._image_file:
            # self.process(image_path, self._output_path)
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
        self.colorConvertAllImage()
        self._cur_image_index -= 1      #实际数量
