import cv2
import utils.imageProcess
from PIL import Image
import numpy as np

class ShearImage(utils.imageProcess.ImageProcess):
    def __init__(self, parent=None):
        super(ShearImage, self).__init__(parent)
        self.shear_matrix = np.array([[1, 0.2, 0], [0.2, 1, 0], [0, 0, 1]])

    def process(self, input_image_path, output_image_path):
        # 加载图像
        image = cv2.imread(input_image_path)
        h, w = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(image, 1)

        if image is None:
            print("无法加载图像，请检查路径！")
            return
        # 斜切图像
        cv_sheared = cv2.warpPerspective(image, self.shear_matrix, (w, h))
        # 转为灰度图像
        cv_sheared = cv2.cvtColor(cv_sheared, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(cv_sheared, 2)
        self._save_single_frame(cv_sheared, self._save_path)

    def bilinear_shear(self, img, kx=0, ky=0):
        """
        实现基于双线性插值的图像斜切
        :param img: 输入图像
        :param kx: 水平方向的斜切因子
        :param ky: 垂直方向的斜切因子
        :return: 斜切后的图像
        """
        src_h, src_w = img.shape[:2]

        # 计算目标图像的尺寸
        dst_w = int(src_w + abs(kx) * src_h)
        dst_h = int(src_h + abs(ky) * src_w)

        # 初始化目标图像
        if len(img.shape) == 3:
            channels = img.shape[2]
            output = np.zeros((dst_h, dst_w, channels), dtype=np.uint8)
        else:
            channels = 1
            output = np.zeros((dst_h, dst_w), dtype=np.uint8)

        # 反向映射 + 双线性插值
        for dst_y in range(dst_h):
            for dst_x in range(dst_w):
                # 反向映射到源图像坐标
                src_x = dst_x - kx * dst_y
                src_y = dst_y - ky * dst_x

                if 0 <= src_x < src_w and 0 <= src_y < src_h:
                    x0 = int(np.floor(src_x))
                    x1 = min(x0 + 1, src_w - 1)
                    y0 = int(np.floor(src_y))
                    y1 = min(y0 + 1, src_h - 1)

                    dx = src_x - x0
                    dy = src_y - y0

                    if channels == 1:
                        val = (1 - dx) * (1 - dy) * img[y0, x0] + \
                            dx * (1 - dy) * img[y0, x1] + \
                            (1 - dx) * dy * img[y1, x0] + \
                            dx * dy * img[y1, x1]
                        output[dst_y, dst_x] = int(val)
                    else:
                        for c in range(channels):
                            val = (1 - dx) * (1 - dy) * img[y0, x0, c] + \
                                dx * (1 - dy) * img[y0, x1, c] + \
                                (1 - dx) * dy * img[y1, x0, c] + \
                                dx * dy * img[y1, x1, c]
                            output[dst_y, dst_x, c] = int(val)
        
        return output

    def self_process(self, input_image_path, output_image_path):
        # 读取图像
        raw_image = cv2.imread(input_image_path)
        if raw_image is None:
            raise FileNotFoundError("输入图像文件未找到！")
        # 斜切变换
        shear_kx = 0.3  # 水平方向斜切因子
        shear_ky = 0.2  # 垂直方向斜切因子
        shear_image = self.bilinear_shear(raw_image, kx=shear_kx, ky=shear_ky)

        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(raw_image, 1)
        output_image = cv2.cvtColor(shear_image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(output_image, 2)
        self._save_single_frame(shear_image, self._save_path)

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
