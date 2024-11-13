import cv2
import utils.imageProcess

class ColorConvertImage(utils.imageProcess.ImageProcess):
    def __init__(self, parent=None):
        super(ColorConvertImage, self).__init__(parent)


    def process(self, input_image_path, output_image_path):
        # 加载图像
        image = cv2.imread(input_image_path)
        self.sendFrameToUI(image, 1)

        if image is None:
            print("无法加载图像，请检查路径！")
            return

        # 反色处理
        inverted_image = cv2.bitwise_not(image)

        self.sendFrameToUI(inverted_image, 2)
        self._save_single_frame(inverted_image, self._save_path)

    def colorConvertAllImage(self):
        for image_path in self._image_file:
            self.process(image_path, self._output_path)

    def run(self):
        self._cur_image_index = 0
        self._image_file.clear()
        self._save_path = self._makeOutputFolder()      # 
        self.getAllFileName( self._input_path)
        self._image_file.sort(key=self.sort_by_number)
        self.colorConvertAllImage()
        self._cur_image_index -= 1      #实际数量
