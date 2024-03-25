'爬取的字段信息：电影名，评分，封面图，详情url，上映时间，导演，类型，制作国家，语言，片长，电影简介，星星比例，多少人评价，预告片，前五条评论，五张详情图片'
import re  # 写正则表达式来爬取指定的内容
import pandas as ps  # 数据挖掘 数据分析 数据清洗
import requests  # 方便发送http请求，方便处理响应结果
from jsonpath_rw import jsonpath, parse  # 提取关键信息和关键值类似于Xpath
import random   # 随机函数
import time   # 时间
from pymysql import *   #mysql与python交互导入pymysql模块
from sqlalchemy import create_engine  # 连接数据库
from bs4 import BeautifulSoup  # 解析网页(正则表达式）
import json  # 前后端进行数据交互

# 创建数据库连接
engine = create_engine('mysql+pymysql://root:root@localhost:3306/doubanmovie')
                       # 数据库类型+数据库驱动选择 数据库用户名：用户密码@服务器地址 端口/数据库
# pymysql操作流程
def init():
    # 使用pymysql的connect()方法连接数据，返回连接对象。
    conn = connect(host='localhost',user='root',password='123456',database='doubanmovie',port=3306,charset='utf8mb4')
    sql = '''
        create table movies(
            id int primary key auto_increment,
            directors varchar(255), # 字典类型游标
            rate varchar(255),
            title varchar(255),
            casts varchar(255),
            cover varchar(255),
            year varchar(255),
            types varchar(255),
            country varchar(255),
            lang varchar(255),
            time varchar(255),
            moveiTime varchar(255),
            comment_len varchar(255),
            starts varchar(255),
            summary varchar(2555),
            comments text,
            imgList varchar(2555),
            movieUrl varchar(255)
        )
    '''
    cursor = conn.cursor()   # 建立数据库连接操作
    cursor.execute(sql)       # 获得cursor对象
    conn.commit()             # 执行

def save_to_csv(df):  # 将数据保存为csv形式存储 保存在当前目录。 Pandas
    df.to_csv('./datas.csv')   # to_csv（）是DataFrame类的方法，导出数据到csv文件

def save_to_sql():   # 将数据（csv中的文件）存入数据库（数据导入）
   df= ps.read_csv("./datas.csv",index_col=0)  # read_csv()是pandas的方法，读取csv中的文件
   df.to_sql('movies',con=engine,index=False,if_exists ='append')


def spider(spiderTarget,start):
    # 每次调用spider获取20条数据
    #请求头（referer：重定向（反爬虫）   user-agent:用户代理）
    # 反爬措施
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36',   # 用户代理（创建请求对象，包装UA信息）  伪装成谷歌浏览器（应对反爬策略的第一步）
        'Referer':'https://movie.douban.com/tag/',  # 设置从何网页跳转过来的
        'Cookie':'bid=6mHemZBr91A; __gads=ID=f6d1e29943a2289e-2235597b46cf0014:T=1637928036:RT=1637928036:S=ALNI_MbUV2rRDkg5u38czBTVDBFS0PLajA; ll="108305"; _vwo_uuid_v2=D05DF24F53B472D086C01A79B01735762|e5e120c8d217d8191d1303c2a5b5aa04; gr_user_id=6441c017-d74b-422f-af14-93a11a57112d; viewed="4913064_1007305"; __yadk_uid=tajeNgKg6NT6nhEQczKfmecGcZqdVBXY; douban-fav-remind=1; push_noty_num=0; push_doumail_num=0; __utmv=30149280.23512; ap_v=0,6.0; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1645066981%2C%22https%3A%2F%2Faccounts.douban.com%2F%22%5D; _pk_ses.100001.4cf6=*; __utmc=30149280; __utmc=223695111; __utma=30149280.1042859692.1637928038.1645066987.1645068438.20; __utmb=30149280.0.10.1645068438; __utmz=30149280.1645068438.20.7.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; __utma=223695111.1442664133.1641956556.1645066987.1645068438.16; __utmb=223695111.0.10.1645068438; __utmz=223695111.1645068438.16.6.utmcsr=baidu|utmccn=(organic)|utmcmd=organic; dbcl2="235123238:e4NYFPqZtk0"; ck=e_AG; _pk_id.100001.4cf6=023cbddd8ff1a247.1641956556.15.1645068496.1645000944.'
          # cookie判断用户是否已经登录
    }

    # 将参数封装到字典中
    params = {   # requests库  get方法  params    (params和headers都是字典结构，里面写上我们想要发送的信息） params = {'查询参数':'查询参数值'}
        'start':start
    }
    movieAllRes = requests.get(spiderTarget,params=params,headers=headers)
    # print(movieAllRes.text)
    # exit(0)


   # 爬取数据
    movieAllRes = movieAllRes.json()  # json转换为字典，json为一种轻量型的数据格式


    detailUrls = jsonpath.jsonpath(movieAllRes,'$.data..url') # json是一种简单的方法来提取给定json文档的部分内容，用来解析json格式的数据，解析所有的电影详情
    # print(detailUrls)

    moveisInfomation = jsonpath.jsonpath(movieAllRes,'$.data')[0] # 解析所有的电影信息
    for i,moveInfomation in enumerate(moveisInfomation): # enumerata枚举函数，用于一个可遍历的数据对象，一般用在for循环中。
        try:
            resultData = {}   # 请求回来的数据
            # 详情
            resultData['detailLink'] = detailUrls[i]
            # 导演（数组）
            resultData['directors'] = ','.join(moveInfomation['directors'])
            # 评分
            resultData['rate'] = moveInfomation['rate']
            # 影片名
            resultData['title'] = moveInfomation['title']
            # 主演（数组）
            resultData['casts'] = ','.join(moveInfomation['casts'])
            # 封面
            resultData['cover'] = moveInfomation['cover']

            # =================进入详情页====================
            detailMovieRes = requests.get(detailUrls[i], headers=headers)  # 向网站发起请求，并获取响应对象
            # print('ok')
            soup = BeautifulSoup(detailMovieRes.text, 'lxml')

            # 上映年份
            resultData['year'] = re.findall(r'[(](.*?)[)]',soup.find('span', class_='year').get_text())[0]  # 全部匹配，返回列表，soup.find以list的形式返回找到的所有标签
            # print(resultData['year'])
            # exit(0)

            types = soup.find_all('span',property='v:genre')  # 输出所有的信息
            for i,span in enumerate(types):
                types[i] = span.get_text()
            # 影片类型（数组）
            resultData['types'] = ','.join(types)
            country = soup.find_all('span',class_='pl')[4].next_sibling.strip().split(sep='/')
            for i,c in enumerate(country):
                country[i] = c.strip()
            # 制作国家（数组）
            resultData['country'] = ','.join(country)
            lang = soup.find_all('span', class_='pl')[5].next_sibling.strip().split(sep='/')
            for i, l in enumerate(lang):
                lang[i] = l.strip()
            # 影片语言（数组）
            resultData['lang'] = ','.join(lang)

            upTimes = soup.find_all('span',property='v:initialReleaseDate')
            upTimesStr = ''
            for i in upTimes:
                upTimesStr = upTimesStr + i.get_text()
            upTime = re.findall(r'\d*-\d*-\d*',upTimesStr)[0]
            # 上映时间
            resultData['time'] = upTime
            if soup.find('span',property='v:runtime'):
                # 时间长度
                resultData['moveiTime'] = re.findall(r'\d+',soup.find('span',property='v:runtime').get_text())[0]
            else:
                # 时间长度
                resultData['moveiTime'] = random.randint(39,61)
            # 评论个数
            resultData['comment_len'] = soup.find('span',property='v:votes').get_text()
            starts = []
            startAll = soup.find_all('span',class_='rating_per') # soup.find_all找到表格
            for i in startAll:
                starts.append(i.get_text())
            # 星星比例（数组）
            resultData['starts'] = ','.join(starts)
            # 影片简介
            resultData['summary'] = soup.find('span',property='v:summary').get_text().strip()

            # 五条热评
            comments_info = soup.find_all('span', class_='comment-info')
            comments = [{} for x in range(5)]
            for i, comment in enumerate(comments_info):
                comments[i]['user'] = comment.contents[1].get_text()
                comments[i]['start'] = re.findall('(\d*)', comment.contents[5].attrs['class'][0])[7]
                comments[i]['time'] = comment.contents[7].attrs['title']
            contents = soup.find_all('span', class_='short')
            for i in range(5):
                comments[i]['content'] = contents[i].get_text()
            resultData['comments'] = json.dumps(comments)  # 在内存中将python对象转化为json格式的字符串

            # 五张详情图
            imgList = []
            lis = soup.select('.related-pic-bd img')
            for i in lis:
                imgList.append(i['src'])
            resultData['imgList'] = ','.join(imgList)
            # =================详情页结束===================


            # =================进入电影页===================
            if soup.find('a',class_='related-pic-video'):
                movieUrl = soup.find('a', class_='related-pic-video').attrs['href']
                foreshowMovieRes = requests.get(movieUrl,headers=headers)
                foreshowMovieSoup = BeautifulSoup(foreshowMovieRes.text,'lxml') # 使用Beautiful Soup对网页进行解析，通过soup操作方法提取相关数据，解析html
                movieSrc = foreshowMovieSoup.find('source').attrs['src'] # 返回查询到的第一个结点
                # 电影路径
                resultData['movieUrl'] = movieSrc
            else:
                resultData['movieUrl'] = '0'

            # =================进入电影页结束===================
            result.append(resultData)
            # print('已经爬取%d条数据' % len(result))
        except :
            # print('!!')
            return

    page = int(start / 20 + 1)  # 每次获取20条数据
    # if not len(result) >= 20:
    #     spider(spiderTarget,page * 20)



# 主页面数据清洗
def main():
    global result
    result = []
    for i in range(12,20):
        print('开始爬取第%s个20' % i)
        page = i
        spider(spiderTarget, page * 20)

        time.sleep(3)   # sleep() 方法暂停给定秒数后执行程序
        print(result)
        df = ps.DataFrame(result) # 导入csv文件
        save_to_csv(df)
        print('导入csv成功......')
        time.sleep(3)
        save_to_sql()
        print('导入sql成功......')
        result = []
        for i in range(len(result)):
            result.pop()

if __name__ == '__main__':
    print('爬虫已开始...')
    spiderTarget = 'https://movie.douban.com/j/new_search_subjects?'
    main()


