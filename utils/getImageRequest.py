import os
import shutil
import cv2

import requests
import os
import re
import numpy as np
from PyQt5.QtCore import QThread,  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap
            

class GetImageFromNetwork(QThread):
    # 信号
    sendRawImageToWidget = pyqtSignal(QPixmap)
    sendCurFrameToWidget = pyqtSignal(int)
    sendImageIndexToWidget = pyqtSignal(int, int)
    sendCameraMsgToWidget = pyqtSignal(int, int, int, int, str, str)

    def __init__(self, append_header=True, header_path='overlay.h265', parent=None):
        super(GetImageFromNetwork, self).__init__(parent)
     
        self._output_path = ''
        self._save_format = ''
        self._save_dir = ''
        self._frame_Idx = 0
        self._image_num = 0
        self._keyword = str
      
    # 设置 _save_format
    def setSaveFormat(self, format_):
        print(format_)
        self._save_format = format_
        self._frame_Idx = 0

    # 设置_image_num
    def setImageNum(self, frameNum):
        self._image_num = frameNum
        print(frameNum)

    # 设置输出文件的路径
    def setOutputPath(self, path):
        self._output_path = path
        self._frame_Idx = 0
        print('output path=', self._output_path)

    # 设置爬取的关键字
    def setKeyword(self, keyword):
        self._keyword = keyword
        print(keyword)
    
    def _makeOutputFolder(self, folder_name):
        save_path = os.path.join(self._output_path, folder_name)
        print("_output_path:",self._output_path)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        else:
            shutil.rmtree(save_path)
            os.makedirs(save_path)
        return save_path
        
    def _saveSigleFrame(self,frame, path):
        if self._save_format == 'png':
            filename = os.path.join(path, f'{self._frame_Idx}.png')
            print(filename)
            cv2.imwrite(filename, frame)

        elif self._save_format == 'jpg':
            filename = os.path.join(path, f'{self._frame_Idx}.jpg')
            print(filename)
            cv2.imwrite(filename, frame)

        elif self._save_format == 'yuv':
            filename = os.path.join(path, f'{self._frame_Idx}.yuv')
            yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
            # height, width, _ = frame.shape
            # print("宽度:", width)
            # print("高度:", height)
            # 将 YUV 数据写入文件
            with open(filename, 'wb') as f:
                f.write(yuv_frame.tobytes())

        self._frame_Idx+=1

    def sendFrameToUI(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV 默认使用BGR格式，转换成RGB格式
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendRawImageToWidget.emit(pixmap)
        self.sendCameraMsgToWidget.emit(0, 0, pixmap.width(), pixmap.height(), self._save_format, " ")

    def get_images_from_baidu(self, keyword, page_num):
        header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'}
        # 请求的 url
        url = 'https://image.baidu.com/search/acjson?'
        n = 0
        self._save_dir = self._makeOutputFolder(self._keyword)       # 创建保存的目录
        print("save_dir:", self._save_dir)
        for pn in range(0, 30 * page_num, 30):
            # 请求参数
            param = {'tn': 'resultjson_com',
                    'logid': '7603311155072595725',
                    'ipn': 'rj',
                    'ct': 201326592,
                    'is': '',
                    'fp': 'result',
                    'queryWord': keyword,
                    'cl': 2,
                    'lm': -1,
                    'ie': 'utf-8',
                    'oe': 'utf-8',
                    'adpicid': '',
                    'st': -1,
                    'z': '',
                    'ic': '',
                    'hd': '',
                    'latest': '',
                    'copyright': '',
                    'word': keyword,
                    's': '',
                    'se': '',
                    'tab': '',
                    'width': '',
                    'height': '',
                    'face': 0,
                    'istype': 2,
                    'qc': '',
                    'nc': '1',
                    'fr': '',
                    'expermode': '',
                    'force': '',
                    'cg': '',    # 这个参数没公开，但是不可少
                    'pn': pn,    # 显示：30-60-90
                    'rn': '30',  # 每页显示 30 条
                    'gsm': '1e',
                    '1618827096642': ''
                    }
            request = requests.get(url=url, headers=header, params=param)
            if request.status_code == 200:
                print('Request success.')
            request.encoding = 'utf-8'
            # 正则方式提取图片链接
            html = request.text
            image_url_list = re.findall('"thumbURL":"(.*?)",', html, re.S)
    
            for image_url in image_url_list:
                image_data = requests.get(url=image_url, headers=header).content
                # 将图像数据解码为 OpenCV 的图像对象
                nparr = np.frombuffer(image_data, np.uint8)
                img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img_np is None:
                    continue
                self._saveSigleFrame(img_np, self._save_dir)
                self.sendFrameToUI(img_np)
                # with open(os.path.join(save_dir, f'{n:06d}.jpg'), 'wb') as fp:
                #     fp.write(image_data)
                n = n + 1 
                if n < self._image_num: 
                    self.sendImageIndexToWidget.emit(n, self._image_num)
                else:
                    return

    def run(self):
        self.get_images_from_baidu(self._keyword, int(self._image_num/30)+1)

     # 下一张图片
    def changeImageBackward(self):
        self._frame_Idx += 1
        image_index_path = os.path.join(self._save_dir, f'{self._frame_Idx}.{self._save_format}')
        if self._frame_Idx < self._image_num:
            pixmap = QPixmap(image_index_path)
            self.sendRawImageToWidget.emit(pixmap)
        else:
            image_index_path = os.path.join(self._save_dir, f'{0}.{self._save_format}')
            pixmap = QPixmap(image_index_path)
            self.sendRawImageToWidget.emit(pixmap)
            self._frame_Idx = 0
        self.sendCameraMsgToWidget.emit(0, 0, pixmap.width(), pixmap.height(), self._save_format, " ")
        self.sendImageIndexToWidget.emit(self._frame_Idx, self._image_num)
            
    # 上一张图片
    def changeImageForward(self):
        self._frame_Idx -= 1
        image_index_path = os.path.join(self._save_dir, f'{self._frame_Idx}.{self._save_format}')
        if self._frame_Idx < 0:
            image_index_path = os.path.join(self._save_dir, f'{self._image_num-1}.{self._save_format}')
            pixmap = QPixmap(image_index_path)
            self.sendRawImageToWidget.emit(pixmap)
            self._frame_Idx = self._image_num-1
        else:
            pixmap = QPixmap(image_index_path)
            self.sendRawImageToWidget.emit(pixmap)
        self.sendCameraMsgToWidget.emit(0, 0, pixmap.width(), pixmap.height(), self._save_format, " ")
        self.sendImageIndexToWidget.emit(self._frame_Idx, self._image_num)
