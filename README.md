# CV-APP

1. Bring up app
  ![image-20241120200039979](assets/image-20241120200039979.png)
  account:PW
  password:1314
  After entering the password,the following interface is displayed

2. 从视频中获取每一帧

  ![image-20241120200233656](assets/image-20241120200233656.png)

3. 从网上爬取图片数据

  ![image-20241120200304172](assets/image-20241120200304172.png)

4. 格式转换

  ![image-20241120200637324](assets/image-20241120200637324.png)

5. 图像缩放

  ![image-20241120200618484](assets/image-20241120200618484.png)

6. 图像灰度化

  ![image-20241120200839688](assets/image-20241120200839688.png)

7. 图像反色

  ![image-20241120200657826](assets/image-20241120200657826.png)

8. 图像旋转

  ![image-20241120200708485](assets/image-20241120200708485.png)

9. 图像斜切

  ![image-20241120200716686](assets/image-20241120200716686.png)

10. 图像透视

  ![image-20241120200728218](assets/image-20241120200728218.png)

11. 直方图均衡化

   ![image-20241120200738212](assets/image-20241120200738212.png)

12. 图像锐化

   ![image-20241120200745939](assets/image-20241120200745939.png)

13. 图像滤波

   ![image-20241120200758133](assets/image-20241120200758133.png)

14. 中值滤波

   ![image-20241120200808465](assets/image-20241120200808465.png)

```bash
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