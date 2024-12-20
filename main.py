import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QDialog, QBoxLayout,QDesktopWidget, QMessageBox,  QFileDialog, QVBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, pyqtSlot, QByteArray, pyqtSignal, QObject, QTimer, QSysInfo
from PyQt5.QtNetwork import QUdpSocket, QNetworkInterface, QAbstractSocket, QHostAddress

import ui.logui
import ui.widget

import apps.logInit
import apps.setupLabelImg

import utils.scrollText
import utils.getImageRequest
import utils.readMp4File
import utils.readImageFile
import utils.format_conversion
import utils.viewImage

import utils.grayscaleImage
import utils.colorConvertImage
import utils.spinImage
import utils.shearImage
import utils.perspectiveImage
import utils.equalizeHistImage
import utils.sharpeningImage
import utils.filterImage
import utils.medianBlurImage


class CV_Widget(QWidget, ui.widget.Ui_Form):
    sendChangeShowToChart = pyqtSignal(int)

    def __init__(self):
        super(CV_Widget, self).__init__()
         # 调用 setupUi 方法设置当前窗口的界面
        self.setupUi(self)

        self.images_view = utils.viewImage.ViewImage()
        self.images_format_cvt = utils.format_conversion.FormatConversion()
        self.images_read = utils.readImageFile.GetImageFromFile()
        self.images_network = utils.getImageRequest.GetImageFromNetwork()
        self.images_mp4 = utils.readMp4File.FrameExtract()

        self.images_grayscale = utils.grayscaleImage.GrayscaleImage()
        self.images_color_convert = utils.colorConvertImage.ColorConvertImage()
        self.images_spin = utils.spinImage.SpinImage()
        self.images_shear = utils.shearImage.ShearImage()
        self.images_perspective = utils.perspectiveImage.PerspectiveImage()
        self.images_equalizeHist = utils.equalizeHistImage.EqualizeHistImage()
        self.images_sharpening = utils.sharpeningImage.SharpeningImage()
        self.images_filter = utils.filterImage.FilterImage()
        self.images_medianBlur = utils.medianBlurImage.MedianBlurImage()

        self.format_list = ['jpg', 'png', 'yuv']
        self.sharping_mode_list = ['roberts', 'sobel', 'laplace']
        self.filter_types_list = ['lowpass', 'highpass']
        self.filter_names_list = ['ideal','butterworth', 'gaussian']
        self.current_format = ['png', 'jpg', 'yuv420p', 'yuv420sp']
        self.convert_format = ['png', 'jpg', 'yuv420p', 'yuv420sp']
        self.input_file = ''
        self._output_file = ''
        self.frame_num = 0
        self.cur_tabwidget_index = 0
        self.cur_listwidget_index = 0
        self.__initUI()

    def __initUI(self):
        self.setScrollText()
           # 遍历每个format条目
        for entry in self.format_list:
            self.comboBox_3.addItem(entry)
            self.comboBox_4.addItem(entry)
        for entry in self.current_format:   
            self.comboBox_8.addItem(entry)
        for entry in self.convert_format:
            self.comboBox_9.addItem(entry)
        # 初始化图像锐化的模式选择
        for entry in self.sharping_mode_list:   
            self.comboBox_5.addItem(entry)
        for entry in self.filter_types_list:   
            self.comboBox.addItem(entry)
        for entry in self.filter_names_list:   
            self.comboBox_2.addItem(entry)
            
        self.spinBox_5.setRange(-1, 99999)
        self.spinBox_6.setRange(-1, 99999)
        self.spinBox_8.setRange(-1, 99999)
        self.spinBox_5.setValue(11)
        self.spinBox_6.setValue(-1)
        self.spinBox_8.setValue(50)

        self.progressBar_3.setRange(0, 100)  # 设置进度条范围
        self.progressBar_3.setValue(0)
        self.progressBar_4.setRange(0, 100)  # 设置进度条范围
        self.progressBar_4.setValue(0)
        self.progressBar_5.setRange(0, 100)  # 设置进度条范围
        self.progressBar_5.setValue(0)
        self.progressBar_6.setRange(0, 100)  # 设置进度条范围
        self.progressBar_6.setValue(0)

        self.lineEdit_7.setText("0")
        self.lineEdit_6.setText("0")

        self.setWindowOpacity(0.96)

        # 设置窗口标题
        self.setWindowTitle("图像处理工具")
        
        self.pushButton_9.clicked.connect(self.selectSavePath)
        self.pushButton_10.clicked.connect(self.start)
        self.pushButton_11.clicked.connect(self.selectFiles)
        self.pushButton_12.clicked.connect(self.reset)
        self.pushButton_13.clicked.connect(self.selectSavePath)
        self.pushButton_14.clicked.connect(self.start)
        self.pushButton_15.clicked.connect(self.start)
        self.pushButton_16.clicked.connect(self.selectInputPath)
        self.pushButton_17.clicked.connect(self.changeImageBackward)
        self.pushButton_18.clicked.connect(self.changeImageForward)
        self.pushButton_19.clicked.connect(self.changeImageBackward)
        self.pushButton_20.clicked.connect(self.changeImageForward)
        self.pushButton_21.clicked.connect(self.changeImageBackward)
        self.pushButton_22.clicked.connect(self.changeImageForward)
        self.pushButton_23.clicked.connect(self.changeImageBackward)
        self.pushButton_24.clicked.connect(self.changeImageForward)
        self.pushButton_25.clicked.connect(self.selectSavePath)
        self.pushButton_26.clicked.connect(self.start)
        self.pushButton_27.clicked.connect(self.selectInputPath)
        self.pushButton_28.clicked.connect(self.reset)
        self.pushButton_29.clicked.connect(self.selectSavePath)
        self.pushButton_30.clicked.connect(self.start)
        self.pushButton_31.clicked.connect(self.selectInputPath)
        self.pushButton_32.clicked.connect(self.reset)
        
        # 12/13/14
        self.pushButton_33.clicked.connect(self.selectSavePath) 
        self.pushButton_34.clicked.connect(self.start)
        self.pushButton_35.clicked.connect(self.selectInputPath)
        self.pushButton_36.clicked.connect(self.reset)
        # 17/18/19
        self.pushButton_37.clicked.connect(self.selectSavePath) 
        self.pushButton_38.clicked.connect(self.start)
        self.pushButton_39.clicked.connect(self.selectInputPath)
        self.pushButton_40.clicked.connect(self.reset)

        self.listWidget.currentRowChanged.connect(self.set_current_list_index)
        self.listWidget_2.currentRowChanged.connect(self.set_current_list_index)
        self.listWidget_3.currentRowChanged.connect(self.set_current_list_index)
        self.listWidget_6.currentRowChanged.connect(self.set_current_list_index)
        self.tabWidget.currentChanged.connect(self.set_current_tab_index) 

        self.listWidget.currentRowChanged.connect(self.stackedWidget.setCurrentIndex)
        # self.listWidget_2.currentRowChanged.connect(self.stackedWidget_2.setCurrentIndex)
        self.listWidget_3.currentRowChanged.connect(self.stackedWidget_3.setCurrentIndex)

        self.listWidget_6.currentRowChanged.connect(self.stackedWidget_6.setCurrentIndex)

        self.images_mp4.sendCameraMsgToWidget.connect(self.receiveVideoInfo)
        self.images_mp4.sendCurFrameIndexToWidget.connect(self.showSchedule)
        self.images_mp4.sendRawImageToWidget.connect(self.showImage)


        self.images_network.sendRawImageToWidget.connect(self.showImage)
        self.images_network.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_network.sendCameraMsgToWidget.connect(self.receiveVideoInfo)

        self.images_read.sendRawImageToWidget.connect(self.showImage)
        self.images_read.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_read.sendDetailImageToWidget.connect(self.showDetailImage)
        
        self.images_grayscale.sendRawImageToWidget.connect(self.showImage)
        self.images_grayscale.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_grayscale.sendDetailImageToWidget.connect(self.showDetailImage)
        
        self.images_color_convert.sendRawImageToWidget.connect(self.showImage)
        self.images_color_convert.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_color_convert.sendDetailImageToWidget.connect(self.showDetailImage)
        
        self.images_spin.sendRawImageToWidget.connect(self.showImage)
        self.images_spin.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_spin.sendDetailImageToWidget.connect(self.showDetailImage)

        self.images_shear.sendRawImageToWidget.connect(self.showImage)
        self.images_shear.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_shear.sendDetailImageToWidget.connect(self.showDetailImage)
        
        self.images_equalizeHist.sendRawImageToWidget.connect(self.showImage)
        self.images_equalizeHist.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_equalizeHist.sendDetailImageToWidget.connect(self.showDetailImage)
        self.images_equalizeHist.sendImagesToWidget.connect(self.showOtherImage)
        
        self.images_perspective.sendRawImageToWidget.connect(self.showImage)
        self.images_perspective.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_perspective.sendDetailImageToWidget.connect(self.showDetailImage)
        
        self.images_sharpening.sendRawImageToWidget.connect(self.showImage)
        self.images_sharpening.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_sharpening.sendDetailImageToWidget.connect(self.showDetailImage)
        self.images_sharpening.sendImagesToWidget.connect(self.showOtherImage)

        self.images_filter.sendRawImageToWidget.connect(self.showImage)
        self.images_filter.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_filter.sendDetailImageToWidget.connect(self.showDetailImage)
        self.images_filter.sendImagesToWidget.connect(self.showOtherImage)

        self.images_medianBlur.sendRawImageToWidget.connect(self.showImage)
        self.images_medianBlur.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_medianBlur.sendDetailImageToWidget.connect(self.showDetailImage)
        self.images_medianBlur.sendImagesToWidget.connect(self.showOtherImage)

        self.images_format_cvt.sendRawImageToWidget.connect(self.showImage)
        self.images_format_cvt.sendImageIndexToWidget.connect(self.showSchedule)

        self.images_view.sendRawImageToWidget.connect(self.showImage)
        self.images_view.sendImageIndexToWidget.connect(self.showSchedule)
        self.images_view.sendCameraMsgToWidget.connect(self.receiveVideoInfo)

      # 显示主窗口
    def showMainWindow(self, val):
        if val == 1:
            self.show()
        else:
            QMessageBox.warning(None, "登录失败", "密码错误", QMessageBox.Yes, QMessageBox.Yes)

    def setScrollText(self):
        self.scroll_text_select_file_00 = utils.scrollText.ScrollTextWindow(self.widget_22, (0,75,255,30))
        self.scroll_text_save_path_00 = utils.scrollText.ScrollTextWindow(self.widget_21, (0,75,255,30))
        self.scroll_text_save_path_01 = utils.scrollText.ScrollTextWindow(self.widget_28, (0,75,255,30))
        self.scroll_text_select_path_21 = utils.scrollText.ScrollTextWindow(self.widget_35, (0,75,255,30))
        self.scroll_text_save_path_11 = utils.scrollText.ScrollTextWindow(self.widget_54, (0,75,255,30))
        self.scroll_text_select_path_11 = utils.scrollText.ScrollTextWindow(self.widget_55, (0,75,255,30))
        self.scroll_text_save_path_10 = utils.scrollText.ScrollTextWindow(self.widget_45, (0,75,255,30))
        self.scroll_text_select_path_10 = utils.scrollText.ScrollTextWindow(self.widget_46, (0,75,255,30))
        
        self.scroll_text_save_path_12_3 = utils.scrollText.ScrollTextWindow(self.widget_60, (0,75,255,30))
        self.scroll_text_select_path_12_3 = utils.scrollText.ScrollTextWindow(self.widget_61, (0,75,255,30))
        
        self.scroll_text_save_path_15_7 = utils.scrollText.ScrollTextWindow(self.widget_64, (0,75,255,30))
        self.scroll_text_select_path_15_7 = utils.scrollText.ScrollTextWindow(self.widget_65, (0,75,255,30))

    def set_current_list_index(self, index):
        self.label_57.setText("NO DATA")
        self.label_90.setText("NO DATA")
        self.label_66.setText("NO DATA")
        self.label_91.setText("NO DATA")
        self.label_73.setText("NO DATA")
        self.label_79.setText("NO DATA")
        self.label_84.setText("NO DATA")
        self.label_85.setText("NO DATA")
        self.label_146.setText("NO DATA")
        self.label_147.setText("NO DATA")
        self.label_148.setText("NO DATA")
        self.cur_listwidget_index = index
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 0:
            self.stackedWidget_2.setCurrentIndex(0)
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 1:
            self.stackedWidget_2.setCurrentIndex(1)
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 2:
            self.stackedWidget_2.setCurrentIndex(2)
            self.scroll_text_select_path_12_3.setText(self.images_grayscale._input_path)
            self.label_139.setText("")
            self.scroll_text_save_path_12_3.setText(self.images_grayscale._output_path)
            self.label_138.setText("")
            self.label_131.setText("图像灰度化:将左边图片进行灰度化处理")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 3:
            self.stackedWidget_2.setCurrentIndex(2)
            self.scroll_text_select_path_12_3.setText(self.images_color_convert._input_path)
            self.label_139.setText("")
            self.scroll_text_save_path_12_3.setText(self.images_color_convert._output_path)
            self.label_138.setText("")
            self.label_131.setText("图像反色：将左边图片进行图像反色处理")
            self.label_86.setText("图像反色")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 4:
            self.stackedWidget_2.setCurrentIndex(2)
            self.scroll_text_select_path_12_3.setText(self.images_spin._input_path)
            self.label_139.setText("")
            self.scroll_text_save_path_12_3.setText(self.images_spin._output_path)
            self.label_138.setText("")
            self.label_131.setText("图像旋转:将图片进行90°旋转")
            self.label_86.setText("图像旋转")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 5:
            self.stackedWidget_2.setCurrentIndex(2)
            self.scroll_text_select_path_12_3.setText(self.images_shear._input_path)
            self.label_139.setText("")
            self.scroll_text_save_path_12_3.setText(self.images_shear._output_path)
            self.label_138.setText("")
            self.label_131.setText("图像斜切:将图片进行斜切")
            self.label_86.setText("图像斜切")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 6:
            self.stackedWidget_2.setCurrentIndex(2)
            self.scroll_text_select_path_12_3.setText(self.images_perspective._input_path)
            self.label_139.setText("")
            self.scroll_text_save_path_12_3.setText(self.images_perspective._output_path)
            self.label_138.setText("")
            self.label_131.setText("图像透视:将图片进行透视")
            self.label_86.setText("图像透视")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 7:
            self.label_3.setText("原始图片直方图")
            self.label_4.setText("处理后的直方图")
            self.stackedWidget_2.setCurrentIndex(3)
            self.stackedWidget_4.setCurrentIndex(0)
            self.stackedWidget_5.setCurrentIndex(0)
            self.scroll_text_select_path_15_7.setText(self.images_equalizeHist._input_path)
            self.label_145.setText("")
            self.scroll_text_save_path_15_7.setText(self.images_equalizeHist._output_path)
            self.label_144.setText("")
            self.label_137.setText("直方图均衡化:将图片进行直方图均衡化")
            self.label_92.setText("直方图均衡化")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 8:
            self.stackedWidget_2.setCurrentIndex(3)
            self.stackedWidget_5.setCurrentIndex(1)
            self.stackedWidget_4.setCurrentIndex(2)
            self.scroll_text_select_path_15_7.setText(self.images_sharpening._input_path)
            self.label_145.setText("")
            self.scroll_text_save_path_15_7.setText(self.images_sharpening._output_path)
            self.label_144.setText("")
            self.label_137.setText("图像锐化:将图片进行锐化")
            self.label_92.setText("图像锐化")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 9:
            self.stackedWidget_2.setCurrentIndex(3)
            self.stackedWidget_5.setCurrentIndex(1)
            self.stackedWidget_4.setCurrentIndex(1)
            self.scroll_text_select_path_15_7.setText(self.images_filter._input_path)
            self.label_145.setText("")
            self.scroll_text_save_path_15_7.setText(self.images_filter._output_path)
            self.label_144.setText("")
            self.label_137.setText("图像滤波:将图片进行滤波")
            self.label_92.setText("图像滤波")
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 10:
            self.label_9.setText("原图")
            self.label_10.setText("加噪声")
            self.label_11.setText("滤波后")
            self.stackedWidget_2.setCurrentIndex(3)
            self.stackedWidget_5.setCurrentIndex(2)
            self.stackedWidget_4.setCurrentIndex(0)
            self.scroll_text_select_path_15_7.setText(self.images_medianBlur._input_path)
            self.label_145.setText("")
            self.scroll_text_save_path_15_7.setText(self.images_medianBlur._output_path)
            self.label_144.setText("")
            self.label_137.setText("中值滤波:将图片进行中值滤波")
            self.label_92.setText("中值滤波")

    def set_current_tab_index(self):
        self.stackedWidget_6.setCurrentIndex(0)
        self.listWidget_6.setCurrentRow(0)
        self.stackedWidget_3.setCurrentIndex(0)
        self.listWidget_3.setCurrentRow(0)
        self.stackedWidget_2.setCurrentIndex(0)
        self.listWidget_2.setCurrentRow(0)
        self.stackedWidget.setCurrentIndex(0)
        self.listWidget.setCurrentRow(0)
        self.cur_tabwidget_index = self.tabWidget.currentIndex()
        self.cur_listwidget_index = 0
   
    # 选择打开文件
    def selectFiles(self):
        # 创建打开文件dialog
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        files, _ = file_dialog.getOpenFileNames(self, "select file", "", "All Files (*)")
        if files:
            for file in files:
                if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 0:
                    self.scroll_text_select_file_00.move_pose(self.label_49)
                    self.scroll_text_select_file_00.setText(file)
                    self.label_49.setText("")
                    self.images_mp4.setInputFilePath(file)
   
    # 选择打开文件
    def selectInputPath(self):
        selected_path = QFileDialog.getExistingDirectory(self, "select path", "")
        if selected_path:
            if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 1:
                self.scroll_text_select_path_21.move_pose(self.label_87)
                self.scroll_text_select_path_21.setText(selected_path)
                self.label_87.setText("")
                self.images_view.setInputFilePath(selected_path)
                self.images_view.start()

            if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 1:
                self.scroll_text_select_path_11.move_pose(self.label_125)
                self.scroll_text_select_path_11.setText(selected_path)
                self.label_125.setText("")
                self.images_read.setInputFilePath(selected_path)

            if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 0:
                self.scroll_text_select_path_10.move_pose(self.label_114)
                self.scroll_text_select_path_10.setText(selected_path)
                self.label_114.setText("")
                self.images_format_cvt.setInputFilePath(selected_path)
            
            if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
                if self.cur_listwidget_index <= 6:
                    self.scroll_text_select_path_12_3.move_pose(self.label_139)
                    self.scroll_text_select_path_12_3.setText(selected_path)
                    self.label_139.setText("")
                    if self.cur_listwidget_index == 2:
                        self.images_grayscale.setInputPath(selected_path)
                    if self.cur_listwidget_index == 3:
                        self.images_color_convert.setInputPath(selected_path)
                    if self.cur_listwidget_index == 4:
                        self.images_spin.setInputPath(selected_path)
                    if self.cur_listwidget_index == 5:
                        self.images_shear.setInputPath(selected_path)
                    if self.cur_listwidget_index == 6:
                        self.images_perspective.setInputPath(selected_path)
                else:
                    self.scroll_text_select_path_15_7.move_pose(self.label_145)
                    self.scroll_text_select_path_15_7.setText(selected_path)
                    self.label_145.setText("")
                    if self.cur_listwidget_index == 7:
                        self.images_equalizeHist.setInputPath(selected_path)
                    if self.cur_listwidget_index == 8:
                        self.images_sharpening.setInputPath(selected_path)
                    if self.cur_listwidget_index == 9:
                        self.images_filter.setInputPath(selected_path)
                    if self.cur_listwidget_index == 10:
                        self.images_medianBlur.setInputPath(selected_path)

    # 选择保存路径
    def selectSavePath(self):
        selected_path = QFileDialog.getExistingDirectory(self, "select path", "")
        if selected_path:
            if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 0:
                self.scroll_text_save_path_00.move_pose(self.label_48)
                self.scroll_text_save_path_00.setText(selected_path)
                self.label_48.setText("")
                self.images_mp4.setOutputPath(selected_path)
            if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 1:
                self.scroll_text_save_path_01.move_pose(self.label_65)
                self.scroll_text_save_path_01.setText(selected_path)
                self.label_65.setText("")
                self.images_network.setOutputPath(selected_path)

            if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 1:
                self.scroll_text_save_path_11.move_pose(self.label_124)
                self.scroll_text_save_path_11.setText(selected_path)
                self.label_124.setText("")
                self.images_read.setOutputPath(selected_path)

            if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 0:
                self.scroll_text_save_path_10.move_pose(self.label_113)
                self.scroll_text_save_path_10.setText(selected_path)
                self.label_113.setText("")
                self.images_format_cvt.setOutputPath(selected_path)
            
            if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
                if self.cur_listwidget_index <= 6:
                    self.scroll_text_save_path_12_3.move_pose(self.label_138)
                    self.scroll_text_save_path_12_3.setText(selected_path)
                    self.label_138.setText("")
                    if self.cur_listwidget_index == 2:
                        self.images_grayscale.setOutputPath(selected_path)
                    if self.cur_listwidget_index == 3:
                        self.images_color_convert.setOutputPath(selected_path)
                    if self.cur_listwidget_index == 4:
                        self.images_spin.setOutputPath(selected_path)
                    if self.cur_listwidget_index == 5:
                        self.images_shear.setOutputPath(selected_path)
                    if self.cur_listwidget_index == 6:
                        self.images_perspective.setOutputPath(selected_path)
                else:
                    self.scroll_text_save_path_15_7.move_pose(self.label_144)
                    self.scroll_text_save_path_15_7.setText(selected_path)
                    self.label_144.setText("")
                    if self.cur_listwidget_index == 7:
                        self.images_equalizeHist.setOutputPath(selected_path)
                    if self.cur_listwidget_index == 8:
                        self.images_sharpening.setOutputPath(selected_path)
                    if self.cur_listwidget_index == 9:
                        self.images_filter.setOutputPath(selected_path)
                    if self.cur_listwidget_index == 10:
                        self.images_medianBlur.setOutputPath(selected_path)

    def start(self):
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 0:
            self.images_mp4.setSaveFormat(self.comboBox_3.currentText())
            self.images_mp4.setInitNum(self.spinBox_6.value(), self.spinBox_5.value())
            self.images_mp4.start()

        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 1:
            self.images_network.setSaveFormat(self.comboBox_4.currentText())
            self.images_network.setImageNum(self.spinBox_8.value())
            self.images_network.setKeyword(self.lineEdit.text())
            self.images_network.start()

        if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 0:
            apps.setupLabelImg.get_main_app(sys.argv) 
        
        if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 1:
            self.images_view.start()
        
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 1:
            self.images_read.setWidthHeight(int(self.lineEdit_5.text()), int(self.lineEdit_4.text()))
            self.images_read.start()

        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 0:
            self.images_format_cvt.setSaveFormat(self.comboBox_8.currentText(), self.comboBox_9.currentText())
            self.images_format_cvt.setWidthHeight(int(self.lineEdit_6.text()), int(self.lineEdit_7.text()))
            self.images_format_cvt.start()
        
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
            if self.cur_listwidget_index == 2:
                self.images_grayscale.start()
                if self.checkBox.isChecked():
                    self.images_grayscale._func_select = 0
                else:
                    self.images_grayscale._func_select = 1
            if self.cur_listwidget_index == 3:
                self.images_color_convert.start()
                if self.checkBox.isChecked():
                    self.images_color_convert._func_select = 0
                else:
                    self.images_color_convert._func_select = 1
            if self.cur_listwidget_index == 4:
                self.images_spin.start()
                if self.checkBox.isChecked():
                    self.images_spin._func_select = 0
                else:
                    self.images_spin._func_select = 1
            if self.cur_listwidget_index == 5:
                self.images_shear.start()
                if self.checkBox.isChecked():
                    self.images_shear._func_select = 0
                else:
                    self.images_shear._func_select = 1
            if self.cur_listwidget_index == 6:
                self.images_perspective.start()
                if self.checkBox.isChecked():
                    self.images_perspective._func_select = 0
                else:
                    self.images_perspective._func_select = 1
            if self.cur_listwidget_index == 7:
                self.images_equalizeHist.start()
                if self.checkBox_3.isChecked():
                    self.images_equalizeHist._func_select = 0
                else:
                    self.images_equalizeHist._func_select = 1
            if self.cur_listwidget_index == 8:
                self.images_sharpening.sharpening_mode = self.comboBox_5.currentText()
                self.images_sharpening.start()
                if self.checkBox_3.isChecked():
                    self.images_sharpening._func_select = 0
                else:
                    self.images_sharpening._func_select = 1
            if self.cur_listwidget_index == 9:
                self.images_filter.filter_types = self.comboBox.currentText()
                self.images_filter.filter_names = self.comboBox_2.currentText()
                self.images_filter.d0 = int(self.lineEdit_2.text())
                self.images_filter.n = int(self.lineEdit_3.text())
                self.images_filter.start()
                if self.checkBox_3.isChecked():
                    self.images_filter._func_select = 0
                else:
                    self.images_filter._func_select = 1
            if self.cur_listwidget_index == 10:
                self.images_medianBlur.start()
                if self.checkBox_3.isChecked():
                    self.images_medianBlur._func_select = 0
                else:
                    self.images_medianBlur._func_select = 1



    def receiveVideoInfo(self, fps, width, height, num_frames, codec, format_video):
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 0:
            self.label_39.setText(f"宽度:{width}")
            self.label_40.setText(f"总帧数:{num_frames}")
            self.label_41.setText(f"高度:{height}")
            self.label_42.setText(f"像素格式:{format_video}")
            self.label_43.setText(f"帧率:{fps}")
            self.label_44.setText(f"编解码器:{codec}")
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 1:
            self.label_56.setText(f"格式:{codec}")
            self.label_58.setText(f"像素宽:{height}")
            self.label_60.setText(f"像素高:{num_frames}")

        if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 1:
            self.label_81.setText(f"格式:{codec}")
            self.label_82.setText(f"像素宽:{height}")
            self.label_83.setText(f"像素高:{num_frames}")

    def showSchedule(self, cur_index, sum_num):
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 0:
            self.label_36.setText(f"{cur_index}/{sum_num+1}")
            self.progressBar_3.setValue(int(cur_index/(sum_num+1)*100))
        if sum_num == 0:
            return
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 1:
            self.label_53.setText(f"{(cur_index+1)}/{sum_num}")
            self.progressBar_4.setValue(int((cur_index+1)/(sum_num)*100))

        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 1:
            self.label_106.setText(f"{(cur_index)}/{sum_num}")
            self.progressBar_7.setValue(int((cur_index)/(sum_num)*100))

        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 0:
            self.label_96.setText(f"{(cur_index)}/{sum_num}")
            self.progressBar_6.setValue(int((cur_index)/(sum_num)*100))
        
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
            if self.cur_listwidget_index <= 6:
                self.label_59.setText(f"{(cur_index)}/{sum_num}")
                self.progressBar_5.setValue(int((cur_index)/(sum_num)*100))
            else:
                self.label_71.setText(f"{(cur_index)}/{sum_num}")
                self.progressBar_8.setValue(int((cur_index)/(sum_num)*100))

        if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 1:
            self.label_78.setText(f"{(cur_index)}/{sum_num}")

    def showImage(self, image):
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 0:
            self.label_35.setPixmap(image.scaled(self.label_35.size()))

        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 1:
            self.label_52.setPixmap(image.scaled(self.label_52.size()))

        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 1:
            self.label_105.setPixmap(image.scaled(self.label_105.size()))

        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 0:
            self.label_95.setPixmap(image.scaled(self.label_95.size()))
        
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
            if self.cur_listwidget_index <= 6:
                self.label_57.setPixmap(image)
            if self.cur_listwidget_index == 7:
                self.label_147.setPixmap(image)
            if self.cur_listwidget_index == 8:
                self.label_73.setPixmap(image)
            if self.cur_listwidget_index == 9:
                self.label_73.setPixmap(image)
            if self.cur_listwidget_index == 10:
                self.label_84.setPixmap(image)
        if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 1:
            self.label_77.setPixmap(image.scaled(self.label_77.size()))
    
    def showDetailImage(self, image):
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 1:
            self.label_126.setPixmap(image.scaled(self.label_126.size()))
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
            if self.cur_listwidget_index <= 6:
                self.label_90.setPixmap(image)
            if self.cur_listwidget_index == 7:
                self.label_148.setPixmap(image)
            if self.cur_listwidget_index == 8:
                self.label_79.setPixmap(image) 
            if self.cur_listwidget_index == 9:
                self.label_79.setPixmap(image)
            if self.cur_listwidget_index == 10:
                self.label_146.setPixmap(image)

    def showOtherImage(self, image, index):
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 7:
            if index == 0:
                self.label_66.setPixmap(image)
            elif index == 1:
                self.label_91.setPixmap(image)
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 8:
            if index == 0:
                self.label_73.setPixmap(image)
            elif index == 1:
                self.label_79.setPixmap(image)

        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 9:
            if index == 0:
                self.label_73.setPixmap(image)
            elif index == 1:
                self.label_79.setPixmap(image)
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index == 10:
            if index == 0:
                self.label_84.setPixmap(image)
            elif index == 1:
                self.label_85.setPixmap(image)
            elif index == 2:
                self.label_146.setPixmap(image)

    def showCameraName(self, name):
        self.label_18.setText(name)
        
    def reset(self):
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 0:
            self.label_39.setText(f"宽度:")
            self.label_40.setText(f"总帧数:")
            self.label_41.setText(f"高度:")
            self.label_42.setText(f"像素格式:")
            self.label_43.setText(f"帧率:")
            self.label_44.setText(f"编解码器:")
            self.label_36.setText(f"1/100")
            self.progressBar_3.setValue(0)
        
    # 上一张图片
    def changeImageBackward(self):
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 1:
            self.images_network.changeImageForward()
        if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 1:
            self.images_view.changeImageForward()
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
            if self.cur_listwidget_index == 2:
                self.images_grayscale.changeImageBackward()
            if self.cur_listwidget_index == 3:
                self.images_color_convert.changeImageBackward()
            if self.cur_listwidget_index == 4:
                self.images_spin.changeImageBackward()
            if self.cur_listwidget_index == 5:
                self.images_shear.changeImageBackward()
            if self.cur_listwidget_index == 6:
                self.images_perspective.changeImageBackward()
            if self.cur_listwidget_index == 7:
                self.images_equalizeHist.changeImageBackward()
            if self.cur_listwidget_index == 8:
                self.images_sharpening.changeImageBackward()
            if self.cur_listwidget_index == 9:
                self.images_filter.changeImageBackward()
            if self.cur_listwidget_index == 10:
                self.images_medianBlur.changeImageBackward()
        
    # 下一张图片
    def changeImageForward(self):
        if self.cur_tabwidget_index == 0 and self.cur_listwidget_index == 1:
            self.images_network.changeImageBackward()
        if self.cur_tabwidget_index == 2 and self.cur_listwidget_index == 1:
            self.images_view.changeImageBackward()
        if self.cur_tabwidget_index == 1 and self.cur_listwidget_index >= 2:
            if self.cur_listwidget_index == 2:
                self.images_grayscale.changeImageForward()
            if self.cur_listwidget_index == 3:
                self.images_color_convert.changeImageForward()
            if self.cur_listwidget_index == 4:
                self.images_spin.changeImageForward()
            if self.cur_listwidget_index == 5:
                self.images_shear.changeImageForward()
            if self.cur_listwidget_index == 6:
                self.images_perspective.changeImageForward()
            if self.cur_listwidget_index == 7:
                self.images_equalizeHist.changeImageForward()
            if self.cur_listwidget_index == 8:
                self.images_sharpening.changeImageForward()
            if self.cur_listwidget_index == 9:
                self.images_filter.changeImageForward()
            if self.cur_listwidget_index == 10:
                self.images_medianBlur.changeImageForward()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    log_ui = apps.logInit.Log_init()
    main_ui = CV_Widget()
    
    log_ui.sendSetUpMainWindowSignal.connect(main_ui.showMainWindow)
    log_ui.show()
    sys.exit(app.exec_())
