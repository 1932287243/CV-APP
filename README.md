1. Bring up app
[图片]
account:PW
password:1314
After entering the password,the following interface is displayed
[图片]
2. Extract pcd and image
Select whether to dedistortion and the topics of the camera and lidar to be extracted. Then, after determining the image format to be saved, the number of frames to skip, and the number of extracted frames, start inputting alignment errors. Finally, select the file path to save and the file path to bagfile. After completing the above operations, you can start extracting.
note:When aligning radar and camera frames, the error should not be too small, otherwise it is difficult to find the aligned data
[图片]
The progress of extraction and alignment can be observed through a progress bar.
[图片]
When the progress bar reaches 100, it indicates that the extraction is complete
[图片]
The final aligned result is located in the output directory of the selected save directory
[图片]
```

报如下错误：

COMLPTTest.py:24: DeprecationWarning: sipPyTypeDict() is deprecated, the extension module should use sipPyTypeDictRef() instead
  class Ui_COMLPTTest(QWidget):
qt.qpa.plugin: Could not load the Qt platform plugin "xcb" in "" even though it was found.
This application failed to start because no Qt platform plugin could be initialized. Reinstalling the application may fix this problem.
 
Available platform plugins are: eglfs, linuxfb, minimal, minimalegl, offscreen, vnc, wayland-egl, wayland, wayland-xcomposite-egl, wayland-xcomposite-glx, webgl, xcb.
 
已放弃
修订方法:

pip install --upgrade sip
pip install --upgrade PyQt5==5.11.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
或者
pip3 install --upgrade PyQt5==5.11.3 -i https://pypi.tuna.tsinghua.edu.cn/simple
                        
原文链接：https://blog.csdn.net/u013934107/article/details/135648672