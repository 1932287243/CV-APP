import cv2
import utils.imageProcess
from PIL import Image
import numpy as np

class PerspectiveImage(utils.imageProcess.ImageProcess):
    def __init__(self, parent=None):
        super(PerspectiveImage, self).__init__(parent)
        self.shear_matrix = np.array([[1, 0.2, 0], [0.2, 1, 0], [0, 0, 1]])
        # self.pts1 = np.float32([[0, 0], [w - 1, 0], [0, h - 1], [w - 1, h - 1]])
        # self.pts2 = np.float32([[0, 0], [w - 1, 50], [50, h - 1], [w - 1, h - 50]])
        # self.persp_matrix = cv2.getPerspectiveTransform(self.pts1, self.pts2)

       

    def process(self, input_image_path, output_image_path):
        # 加载图像
        image = cv2.imread(input_image_path)
        h, w = image.shape[:2]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # 为了显示
        self.sendFrameToUI(image, 1)

        if image is None:
            print("无法加载图像，请检查路径！")
            return
        # 透视变换
        # 定义透视变换矩阵
        src_points = np.float32([[0, 0], [image.shape[1], 0],
                                [0, image.shape[0]], [image.shape[1], image.shape[0]]])
        dst_points = np.float32([[50, 50], [image.shape[1] - 50, 100],
                                [100, image.shape[0] - 50], [image.shape[1] - 50, image.shape[0] - 100]])
        persp_matrix = cv2.getPerspectiveTransform(src_points, dst_points)
        cv_perspective = cv2.warpPerspective(image, persp_matrix, (w, h))
        
        self.sendFrameToUI(cv_perspective, 2)
        cv_perspective = cv2.cvtColor(cv_perspective, cv2.COLOR_BGR2RGB)   # 为了显示
        self._save_single_frame(cv_perspective, self._save_path)

    def bilinear_perspective_transform(self, img, M, dst_shape):
        """
        双线性插值实现图像透视变换
        :param img: 输入图像
        :param M: 3x3 透视变换矩阵
        :param dst_shape: 输出图像的尺寸 (height, width)
        :return: 透视变换后的图像
        """
        src_h, src_w = img.shape[:2]
        dst_h, dst_w = dst_shape

        # 逆矩阵，用于反向映射
        M_inv = np.linalg.inv(M)

        # 初始化输出图像
        if len(img.shape) == 3:
            channels = img.shape[2]
            output = np.zeros((dst_h, dst_w, channels), dtype=np.uint8)
        else:
            channels = 1
            output = np.zeros((dst_h, dst_w), dtype=np.uint8)

        # 遍历目标图像像素进行反向映射和插值
        for dst_y in range(dst_h):
            for dst_x in range(dst_w):
                # 目标图像像素坐标归一化
                target_point = np.array([dst_x, dst_y, 1])

                # 映射到源图像坐标
                src_point = M_inv @ target_point
                src_x = src_point[0] / src_point[2]
                src_y = src_point[1] / src_point[2]

                # 检查是否在源图像范围内
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

                 # 定义透视变换矩阵
        src_points = np.float32([[0, 0], [raw_image.shape[1], 0],
                                [0, raw_image.shape[0]], [raw_image.shape[1], raw_image.shape[0]]])
        dst_points = np.float32([[50, 50], [raw_image.shape[1] - 50, 100],
                                [100, raw_image.shape[0] - 50], [raw_image.shape[1] - 50, raw_image.shape[0] - 100]])
        persp_matrix = cv2.getPerspectiveTransform(src_points, dst_points)

        # 透视变换
        output_image = self.bilinear_perspective_transform(raw_image, persp_matrix, (raw_image.shape[0], raw_image.shape[1]))

        # 显示结果
        raw_image = cv2.cvtColor(raw_image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(raw_image, 1)
        output_image = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
        self.sendFrameToUI(output_image, 2)
        self._save_single_frame(output_image, self._save_path)

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
