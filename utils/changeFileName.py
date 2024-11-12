import os
import shutil

import os
from PyQt5.QtCore import QThread

        
class ChangeFileName(QThread):
    # 信号

    def __init__(self, parent=None):
        super(ChangeFileName, self).__init__(parent)
        self._intput_path = ''
        # self._save_dir = ''

    # 设置输出文件的路径
    def setInputputPath(self, path):
        self._intput_path = path

    def run(self):
        # 设置目标目录路径（假设目标目录在当前工作目录下的new_folder中）
        target_dir = os.path.join(self._intput_path, "0rename_dir")

        # 如果目标目录不存在，则创建它
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 列出当前目录中的所有文件和文件夹
        entries = os.listdir(self._intput_path)

        # 初始化文件计数器
        file_counter = 0

        for entry in entries:
            # 获取完整的文件路径
            file_path = os.path.join(self._intput_path, entry)
            
            # 检查这个条目是否为文件
            if os.path.isfile(file_path):
                # 分离文件的扩展名
                _, file_extension = os.path.splitext(entry)
                
                # 构造新的文件名，格式为：数字 + 原始扩展名
                new_file_name = f"{file_counter}{file_extension}"
                new_file_path = os.path.join(target_dir, new_file_name)
                
                # 复制并重命名文件到目标目录
                shutil.copy2(file_path, new_file_path)
                print(f"Copied and renamed '{entry}' to '{new_file_path}'")
                
                # 更新文件计数器
                file_counter += 1

