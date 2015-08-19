# Python入门网络爬虫之精华版  

Python学习网络爬虫主要分3个大的版块：**抓取**，**分析**，**存储**  
另外，比较常用的爬虫框架[Scrapy](http://scrapy.org/)，这里最后也介绍一下。    
先列举一下相关参考：[宁哥的小站-网络爬虫](http://www.lining0806.com/category/spider/)  
***

## 抓取  
这一步，你要明确要得到的内容是是什么？是HTML源码，还是Json格式的字符串等等。  

#### 1. 最基本的抓取  
一般属于get请求情况，直接从服务器上获取数据。  
首先，Python中自带urllib及urllib2这两个模块，基本上能满足一般的页面抓取。另外，[requests](https://github.com/kennethreitz/requests)也是非常有用的包，与此类似的，还有[httplib2](https://github.com/jcgregorio/httplib2)等等。    
```
Requests：
	import requests
	response = requests.get(url)
	content = requests.get(url).content # string
	print "response headers:", response.headers # dict
	print "content:", content
Urllib2：
	import urllib2
	response = urllib2.urlopen(url)
	content = urllib2.urlopen(url).read() # string
	print "response headers:", response.headers # not dict
	print "content:", content
Httplib2：
	import httplib2
	http = httplib2.Http()
	response_headers, content = http.request(url, 'GET')
	print "response headers:", response_headers # dict
	print "content:", content
```  
此外，对于带有查询字段的url，get请求一般会将来请求的数据附在url之后，以?分割url和传输数据，多个参数用&连接。  
```
data = {'data1':'XXXXX', 'data2':'XXXXX'} # dict类型
Requests：data为dict，json
	import requests
	response = requests.get(url=url, params=data) # GET请求发送 
Urllib2：data为string
	import urllib, urllib2    
	data = urllib.urlencode(data) # 编码工作，由dict转为string
	full_url = url+'?'+data # GET请求发送
	response = urllib2.urlopen(full_url)
```

### 2. 对于反爬虫机制的处理  

**2.1 模拟登陆情况**  
这种属于post请求情况，先向服务器发送表单数据，服务器再将返回的cookie存入本地。  
```
data = {'data1':'XXXXX', 'data2':'XXXXX'} # dict类型
Requests：data为dict，json
	import requests
	response = requests.post(url=url, data=data) # POST请求发送，可用于用户名密码登陆情况
Urllib2：data为string
	import urllib, urllib2    
	data = urllib.urlencode(data) # 编码工作，由dict转为string
	req = urllib2.Request(url=url, data=data) # POST请求发送，可用于用户名密码登陆情况
	response = urllib2.urlopen(req)
```  

**2.2 使用cookie登陆情况**  
使用cookie登陆，服务器会认为你是一个已登陆的用户，所以就会返回给你一个已登陆的内容。因此，需要验证码的情况可以使用带验证码登陆的cookie解决。  
```
import requests			
requests_session = requests.session() # 创建会话对象requests.session()，可以记录cookie
response = requests_session.post(url=url_login, data=data) # requests_session的POST请求发送，可用于用户名密码登陆情况。必须要有这一步！拿到Response Cookie！
```
若存在验证码，此时采用response = requests_session.post(url=url_login, data=data)是不行的，做法应该如下：  
```
response_captcha = requests_session.get(url=url_login, cookies=cookies)
response1 = requests.get(url_login) # 未登陆
response2 = requests_session.get(url_login) # 已登陆，因为之前拿到了Response Cookie！
response3 = requests_session.get(url_results) # 已登陆，因为之前拿到了Response Cookie！
```
相关参考：[网络爬虫-验证码登陆](http://www.lining0806.com/6-%E7%BD%91%E7%BB%9C%E7%88%AC%E8%99%AB-%E9%AA%8C%E8%AF%81%E7%A0%81%E7%99%BB%E9%99%86/)  
参考项目：[爬取知乎网站](https://github.com/lining0806/ZhihuSpider)  

**2.3 伪装成浏览器，或者反“反盗链”**  
```
headers = {'User-Agent':'XXXXX'} # 伪装成浏览器访问，适用于拒绝爬虫的网站
headers = {'Referer':'XXXXX'} # 反“反盗链”，适用于有“反盗链”的网站
headers = {'User-Agent':'XXXXX', 'Referer':'XXXXX'}
Requests：
	response = requests.get(url=url, headers=headers)
Urllib2：
	import urllib, urllib2   
	req = urllib2.Request(url=url, headers=headers)
	response = urllib2.urlopen(req)
```

### 3. 使用代理  
适用情况：限制IP地址情况，也可解决由于“频繁点击”而需要输入验证码登陆的情况。  
```
proxies = {'http':'http://XX.XX.XX.XX:XXXX'}
Requests：
	import requests
	response = requests.get(url=url, proxies=proxies)
Urllib2：
	import urllib2
	proxy_support = urllib2.ProxyHandler(proxies)
	opener = urllib2.build_opener(proxy_support, urllib2.HTTPHandler)
	urllib2.install_opener(opener) # 安装opener，此后调用urlopen()时都会使用安装过的opener对象
	response = urllib2.urlopen(url)
```

### 4. 对于断线重连  
```
def multi_session(session, *arg):
	while True:
		retryTimes = 20
	while retryTimes>0:
		try:
			return session.post(*arg)
		except:
			print '.',
			retryTimes -= 1
```
或者  
```
def multi_open(opener, *arg):
	while True:
		retryTimes = 20
	while retryTimes>0:
		try:
			return opener.open(*arg)
		except:
			print '.',
			retryTimes -= 1
```
这样我们就可以使用multi_session或multi_open对爬虫抓取的session或opener进行保持。    

### 5. 多进程抓取  
这里针对[华尔街见闻](http://live.wallstreetcn.com/ )进行多进程的实验对比：[Python多进程抓取](https://github.com/lining0806/Spider_Python) 与 [Java多进程抓取](https://github.com/lining0806/Spider)  
相关参考：[关于Python和Java的多进程多线程计算方法对比](http://www.lining0806.com/%E5%85%B3%E4%BA%8Epython%E5%92%8Cjava%E7%9A%84%E5%A4%9A%E8%BF%9B%E7%A8%8B%E5%A4%9A%E7%BA%BF%E7%A8%8B%E8%AE%A1%E7%AE%97%E6%96%B9%E6%B3%95%E5%AF%B9%E6%AF%94/)  

### 6. 对于Ajax请求的处理  
对于“加载更多”情况，使用Ajax来传输很多数据。它的工作原理是：从网页的url加载网页的源代码之后，会在浏览器里执行JavaScript程序。这些程序会加载更多的内容，“填充”到网页里。这就是为什么如果你直接去爬网页本身的url，你会找不到页面的实际内容。  
这里，若使用Google Chrome分析”请求“对应的链接(方法：右键→审查元素→Network→清空，点击”加载更多“，出现对应的GET链接寻找Type为text/html的，点击，查看get参数或者复制Request URL)，循环过程。  
* 如果“请求”之前有页面，依据上一步的网址进行分析推导第1页。以此类推，抓取抓Ajax地址的数据。  
* 对返回的json格式数据(str)进行正则匹配。json格式数据中，需从'\\uxxxx'形式的unicode_escape编码转换成u'\uxxxx'的unicode编码。  
参考项目：[Python多进程抓取](https://github.com/lining0806/Spider_Python)  

### 7. 验证码识别  
对于网站有验证码的情况，我们有三种办法：  

1. 使用代理，更新IP。
2. 使用cookie登陆。
3. 验证码识别。

使用代理和使用cookie登陆之前已经讲过，下面讲一下验证码识别。  
可以利用开源的Tesseract-OCR系统进行验证码图片的下载及识别，将识别的字符传到爬虫系统进行模拟登陆。如果不成功，可以再次更新验证码识别，直到成功为止。  
参考项目：[Captcha1](https://github.com/lining0806/Captcha1)


## 分析  
抓取之后就是对抓取的内容进行分析，你需要什么内容，就从中提炼出相关的内容来。  
常见的分析工具有[正则表达式](http://deerchao.net/tutorials/regex/regex.htm)，[BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)，[lxml](http://lxml.de/)等等。  

## 存储  
分析出我们需要的内容之后，接下来就是存储了。  
我们可以选择存入文本文件，也可以选择存入MySQL或MongoDB数据库等。  

## Scrapy  
Scrapy是一个基于Twisted的开源的Python爬虫框架，在工业中应用非常广泛。  
相关内容可以参考[基于Scrapy网络爬虫的搭建](http://www.lining0806.com/%E5%9F%BA%E4%BA%8Escrapy%E7%BD%91%E7%BB%9C%E7%88%AC%E8%99%AB%E7%9A%84%E6%90%AD%E5%BB%BA/)  
