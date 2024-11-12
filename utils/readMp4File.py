import os
import shutil
import cv2

import ffmpeg

from cv2 import VideoCapture
from PyQt5.QtCore import QThread,  pyqtSignal
from PyQt5.QtGui import QImage,  QPixmap



class FrameExtract(QThread):
    # # 生成exe标志
    # INSTALL == 1
    # 信号
    sendRawImageToWidget = pyqtSignal(QPixmap)
    sendCameraMsgToWidget = pyqtSignal(int, int, int, int, str, str)
    # sendImageIndexToWidget = pyqtSignal(int, int)
    sendCurFrameIndexToWidget = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(FrameExtract, self).__init__(parent)
        self._video_input_str = ''
        self._output_path = '~/Downloads'
        self._frameIdx = 0
        self._frameNum = -1
        self.skip_num = 1
        self._save_format = ''
        self._start_flag = 1
      
    # 设置 _save_format
    def setSaveFormat(self, format_):
        self._save_format = format_
        self._frameIdx = 0
        print("MP4 format:", self._save_format)

    # 设置_frameNum
    def setInitNum(self, frameNum, skipNum):
        self._frameNum = frameNum
        self.skip_num = skipNum
        print("MP4 frameNum=", self._frameNum)
        print("MP4 skipNum=", self.skip_num)

    # 设置输入文件的路径
    def setInputFilePath(self, path):
        self._video_input_str = path
        print('MP4 input file=', self._video_input_str)
        self._frameIdx = 0
        # 重新获取视频的详细信息
        self._start_flag = 1    

    # 设置输出文件的路径
    def setOutputPath(self, path):
        self._output_path = path
        print('output path=', self._output_path)
        self._frameIdx = 0

    def get_video(cls, video)->VideoCapture:
        cap = cv2.VideoCapture(video)
        if cap.isOpened():
            return cap
        else:
            raise ValueError("video file can not be opened")
        
    def _make_output_folder(self):
        # 提取视频文件名（不包含扩展名）作为文件夹名称
        folder_name = self._video_input_str.split('.')[0].split('/')[-1]
        print(folder_name)
        path = os.path.join(self._output_path, folder_name)
        print(path)
        if not os.path.exists(path):
            os.makedirs(path)
        else:
            shutil.rmtree(path)
            os.makedirs(path)
        return path
    
    def sendFrameToUI(self, frame):
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # OpenCV 默认使用BGR格式，转换成RGB格式
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.sendRawImageToWidget.emit(pixmap)

    def _save_single_frame(self,frame, path):
        if self._save_format == 'png':
            filename = os.path.join(path, f'{self._frameIdx}.png')
            cv2.imwrite(filename, frame)
        elif self._save_format == 'jpg':
            filename = os.path.join(path, f'{self._frameIdx}.jpg')
            cv2.imwrite(filename, frame)
        elif self._save_format == 'yuv':
            filename = os.path.join(path, f'{self._frameIdx}.yuv')
            yuv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2YUV_I420)
            # height, width, _ = frame.shape
            # print("宽度:", width)
            # print("高度:", height)
            # 将 YUV 数据写入文件
            with open(filename, 'wb') as f:
                f.write(yuv_frame.tobytes())
        # self.sendCurFrameIndexToWidget.emit(self._frameIdx, self._frameNum)
        self._frameIdx+=1
        # self._frameNum =  self._frameIdx
        # self.sendImageIndexToWidget.emit(self._frameIdx,  self._frameNum)

    def get_video_pixel_format(self, video_path):
        try:
            # 获取视频文件的信息
            probe = ffmpeg.probe(video_path)
            # 从视频流信息中提取像素格式
            video_streams = [stream for stream in probe['streams'] if stream['codec_type'] == 'video']
            if video_streams:
                # 假设我们关注第一个视频流
                pixel_format = video_streams[0]['pix_fmt']
                return pixel_format
            else:
                return "未找到视频流"
        except ffmpeg.Error as e:
            print("FFmpeg错误:", e.stderr)
            return None

    def save_frame(self, count:int=-1):
        ret = True
        path = self._make_output_folder()
        cap = cv2.VideoCapture(self._video_input_str)
        # cap = 
        if self._start_flag == 1:
            # 获取视频信息
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # if INSTALL == 0:
            # format_video = self.get_video_pixel_format(self._video_input_str)
            # else:
            format_video = 'yuv420p'
            codec = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
            self.sendCameraMsgToWidget.emit(fps, width, height, num_frames+1, codec, format_video)
            # 打印视频信息
            print(f'视频宽度: {width}')
            print(f'视频高度: {height}')
            print(f'帧率: {fps}')
            print(f'像素格式: {format_video}')
            print(f'总帧数: {num_frames}')
            print(f"视频编解码器: {codec}")
            self._start_flag = 0
        cur_frame = 1
        if cap.isOpened():
            if count<0:
                while ret:
                    ret, frame = cap.read()
                    if ret:
                        self.sendFrameToUI(frame)
                        if cur_frame % self.skip_num == 0:
                            self._save_single_frame(frame, path)
                            # cur_frame = 1
                        cur_frame+=1
                        self.sendCurFrameIndexToWidget.emit(cur_frame/self.skip_num, num_frames/self.skip_num-1)
                #  self._frameNum = cur_frame - 1
            else:
                counter = 0
                while (counter < count) & ret:
                    # counter+=1
                    ret, frame = cap.read()
                    if ret:
                        self.sendFrameToUI(frame)
                        if cur_frame % self.skip_num == 0:
                            self._save_single_frame(frame, path)
                            # cur_frame = 1
                            counter+=1
                        cur_frame+=1
                        self.sendCurFrameIndexToWidget.emit(cur_frame/self.skip_num, num_frames/self.skip_num-1)
                        # self.sendCurFrameIndexToWidget.emit(cur_frame)
                        # if self._saveFlag == 1:
                        #     counter+=1
                        #     self._save_single_frame(frame, path)
                        #     self._saveFlag = 0
                    else:
                        print("something went wrong")
                print("done")
                if not ret:
                    print("Number of frames count more than available frames")
        else:
            raise ValueError("video file can not be opened")
    
    def run(self):
        self._start_flag = 1
        self.save_frame(self._frameNum)






