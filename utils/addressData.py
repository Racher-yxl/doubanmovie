from . import homeData
import pandas as ps                     # 地图分析表
df = ps.DataFrame(homeData.getAllData(),columns=[  # 传入所有数据
        'id',
        'directors',
        'rate',
        'title',
        'casts',
        'cover',
        'year',
        'types',
        'country',
        'lang',
        'time',
        'moveiTime',
        'comment_len',
        'starts',
        'summary',
        'comments',
        'imgList',
        'movieUrl',
        'detailLink'
    ])






def getAddressData():
    addrsses = df['country'].values       # 从数据库中取出所有数据，取国家一栏的数据，进行处理，每个国家有多少个
    address = []
    for i in addrsses:
        if isinstance(i,list):
             for j in i:
                address.append(j)
        else:
                address.append(i)
    addressDic = {}
    for i in address:
        if addressDic.get(i,-1) == -1:
            addressDic[i] = 1
        else:
            addressDic[i] = addressDic[i] + 1
    return list(addressDic.keys()),list(addressDic.values())

def getLangData():                               # 对语言进行处理
    langs = df['lang'].values
    langes = []
    for i in langs:
        if isinstance(i,list):
             for j in i:
                langes.append(j)
        else:
                langes.append(i)
    langsDic = {}
    for i in langes:
        if langsDic.get(i,-1) == -1:
            langsDic[i] = 1
        else:
            langsDic[i] = langsDic[i] + 1
    return list(langsDic.keys()),list(langsDic.values())
