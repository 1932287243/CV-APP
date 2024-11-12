import os
import shutil

import os
from PyQt5.QtCore import QThread, pyqtSignal
from random import sample
            

class SplitFilesRandomly(QThread):
    # 信号
    sendSplitNumToWidget = pyqtSignal(int, int, int, int)

    def __init__(self, parent=None):
        super(SplitFilesRandomly, self).__init__(parent)
        self._intput_path = ''
        self._output_path = ''
        self._train_num = 0
        self._test_num = 0
        self._valid_num = 0

    # 设置输出文件的路径
    def setInputputPath(self, path):
        self._intput_path = path

    def setOutputPath(self, path):
        self._output_path = path
    
    def setNum(self, train_num, test_num, valid_num):
        self._train_num = train_num
        self._test_num = test_num
        self._valid_num = valid_num

    def _makeOutputFolder(self):
        train_path = os.path.join( self._output_path, 'train')
        if not os.path.exists(train_path):
            os.makedirs(train_path)
        else:
            shutil.rmtree(train_path)
            os.makedirs(train_path)
        test_path = os.path.join(self._output_path, 'test')
        if not os.path.exists(test_path):
            os.makedirs(test_path)
        else:
            shutil.rmtree(test_path)
            os.makedirs(test_path)
        valid_path = os.path.join(self._output_path, 'valid')
        if not os.path.exists(valid_path):
            os.makedirs(valid_path)
        else:
            shutil.rmtree(valid_path)
            os.makedirs(valid_path)
       
       
    def copy_files_randomly(self, src_dir, dst_dirs, ratios):
        """
        从源目录随机复制文件到多个目标目录，按照指定的比例。
        
        :param src_dir: 源目录路径
        :param dst_dirs: 目标目录路径列表
        :param ratios: 复制到每个目标目录的文件比例列表
        """
        # # 确保比率总和为1
        # assert sum(ratios) == 1, "Ratios must sum up to 1."
        # 检查ratios之和是否为1
        if sum(ratios) == 1:
            print("Ratios sum up to 1. Proceeding with file distribution.")
        else:
            print("Error: Ratios must sum up to 1.")
        # 获取源目录中所有文件的路径
        all_files = [f for f in os.listdir(src_dir) if os.path.isfile(os.path.join(src_dir, f))]
        
        # 确保文件列表不为空
        if not all_files:
            print("No files found in the source directory.")
            return
        
        # 计算每个部分的文件数量
        file_counts = [int(len(all_files) * ratio) for ratio in ratios]
        
        # 为了确保文件总数正确，对最后一个文件夹进行调整
        file_counts[-1] = len(all_files) - sum(file_counts[:-1])
        
        # 随机选择文件
        selected_files = sample(all_files, len(all_files))
        self.sendSplitNumToWidget.emit(len(all_files),file_counts[0], file_counts[1], file_counts[2])
        start_index = 0
        for dst_dir, count in zip(dst_dirs, file_counts):
            # 创建目标目录（如果不存在）
            os.makedirs(dst_dir, exist_ok=True)
            
            # 选定当前批次的文件
            current_batch = selected_files[start_index:start_index + count]
            
            # 复制文件
            for file_name in current_batch:
                src_file_path = os.path.join(src_dir, file_name)
                dst_file_path = os.path.join(dst_dir, file_name)
                shutil.copy2(src_file_path, dst_file_path)
            
            start_index += count

    def run(self):
        ratios = [0.7, 0.2, 0.1]
        train_path = os.path.join( self._output_path, 'train')
        test_path = os.path.join(self._output_path, 'test')
        valid_path = os.path.join(self._output_path, 'valid')
        dst_directories = [train_path, test_path, valid_path]
        print(dst_directories)
        print(self._intput_path)
        self.copy_files_randomly(self._intput_path, dst_directories, ratios)

