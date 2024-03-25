#基于Python豆瓣电影数据可视化系统设计与实现

主要从数据分析以及系统搭建两个方面入手。 首先研究数据分析经常需要画像的数据, 简单来说就是去做用户刻画的时候, 用户可视化画像可以帮助数据分析刻画用户更加清晰。 其次本课题基于python豆瓣电影数据可视化系统设计与实现，需要从数据分析的数据层、挖掘层、服务层、用户提取进行深度理解，为后期进行系统制作的时候有完整的设计思路。 然后就是功能图像可视化分析，我们可以利用用户画像平台进行快速进行某个功能的用户画像描述分析, 比如豆瓣app 的最新推荐功能, 我们想要知道使用最新推荐的用户是怎么样的用户群体, 以及使用最近推荐不同时长的用户他们的用户特征分别都是怎么样的，就可以快速的进行分析。 最后就是使用echarts制作可视化Web页面。 

#使用方法
（1）数据清洗  
（2）数据探索  
（3）可视化设计  
（4）交互功能   
（5）数据导出  
（6）Python，mysql  
（7）Flask，Pandas，SQLAlchemy，Echarts

#爬虫步骤
##1、发送HTTP请求  
使用requests库向目标网址发送HTTP请求，获取电影列表页面的内容。这里使用了自定义的请求头部headers来模拟浏览器行为，以避免被网站的反爬虫机制识别。  
'''  
headers = {
    'User-Agent': '你的浏览器标识',
    'Referer': 'https://movie.douban.com/tag/',
    'Cookie': '你的Cookie信息'
}
movieAllRes = requests.get(spiderTarget, params=params, headers=headers)  
'''    
##2、内容解析  
使用json方法将获取的内容解析为JSON格式，进而使用jsonpath库提取需要的信息，如电影的详细页面URL、导演、评分等。  
'''  
movieAllRes = movieAllRes.json()
detailUrls = jsonpath.jsonpath(movieAllRes, '$.data..url')
'''
##3. 详细页面数据提取

对于每一部电影，再次使用requests.get方法获取其详细页面的内容，然后使用BeautifulSoup进行HTML内容解析。通过CSS选择器或正则表达式提取电影的上映时间、类型、制作国家等信息。  
'''   
detailMovieRes = requests.get(detailUrls[i], headers=headers)
soup = BeautifulSoup(detailMovieRes.text, 'lxml')
resultData['year'] = re.findall(r'[(](.*?)[)]', soup.find('span', class_='year').get_text())[0]
'''  
##4. 数据存储  
把解析好的数据保存到pandas的DataFrame中，然后将DataFrame存储到CSV文件或直接导入到MySQL数据库。  
'''  
df = ps.DataFrame(result)  # 创建DataFrame
df.to_csv('./datas.csv')  # 保存到CSV
df.to_sql('movies', con=engine, index=False, if_exists='append')  # 保存到MySQL数据库
'''  
##5. 循环与控制  
通过循环控制爬取多个页面的数据，使用time.sleep来减缓爬取速度，避免对目标网站造成过大压力。  
	'''  
for i in range(12, 20):
    spider(spiderTarget, i * 20)
    time.sleep(3)
'''  

#爬取到的字段
	'''  
	爬取数据
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
'''  
	

#保存  
	def save_to_csv(df):  # 将数据保存为csv形式存储 保存在当前目录。 Pandas
    	df.to_csv('./datas.csv')   # to_csv（）是DataFrame类的方法，导出数据到csv文件  

	def save_to_sql():   # 将数据（csv中的文件）存入数据库（数据导入）
   		df= ps.read_csv("./datas.csv",index_col=0)  # read_csv()是pandas的方法，读取csv中的文件  
   		df.to_sql('movies',con=engine,index=False,if_exists ='append')

	
