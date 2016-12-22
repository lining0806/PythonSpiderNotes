### 验证码识别项目第一版：Captcha1

本项目采用Tesseract V3.01版本(V3.02版本在训练时有改动，多shapeclustering过程)  

**Tesseract用法：** 
* 配置环境变量TESSDATA_PREFIX =“D:\Tesseract-ocr\”，即tessdata的目录，在源码中会到这个路径下查找相应的字库文件用来识别。  
* 命令格式：  
`tesseract imagename outputbase [-l lang] [-psm pagesegmode] [configfile...]`  
* 只识别成数字   
`tesseract imagename outputbase -l eng digits`  
* 解决empty page!!  
**-psm N** 

	7 = Treat the image as a single text line  
	tesseract imagename outputbase -l eng -psm 7  
* configfile 参数值为tessdata\configs 和 tessdata\tessconfigs 目录下的文件名：   
`tesseract imagename outputbase -l eng nobatch`  


**验证码识别项目使用方法1：**  
 
* 将下载的图片放到./pic目录下，  

	验证码图片名称：get_random.jpg  
	价格图片名称：get_price_img.png 

* 命令格式：  

	验证码图片识别：python tess_test.py ./pic/get_random.jpg  
	价格图片识别：python tess_test.py ./pic/get_price_img.png
  
打印出识别的结果

若要将结果存在临时文本文件**temp.txt**中，则修改pytessr_pro.py中代码"**cleanup_scratch_flag = True**"改为"**cleanup_scratch_flag = False**"
