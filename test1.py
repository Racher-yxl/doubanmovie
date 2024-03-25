#案例说明
import requests    #导入requests库
from bs4 import BeautifulSoup         #引入BS库

#利用requests.get()获取网页数据
res = requests.get('https://localprod.pandateacher.com/python-manuscript/crawler-html/spider-men5.0.html')
html = res.text          #解析为文本数据
soup = BeautifulSoup(html,'html.parser')        #把网页解析为BeautifulSoup对象
print(type(soup))        #查看类型。结果是一个<class 'bs4.BeautifulSoup'>对象，便于后面提取数据
print(" ")
print(soup)
