from pymysql import *
# 连接数据库
conn = connect(host='localhost',user='root',password='root',database='doubanmovie',port=3306)
cursor = conn.cursor()


def querys(sql,params,type='no_select'):
    params = tuple(params)
    print(sql)
    cursor.execute(sql,params)
    if type != 'no_select':
        data_list = cursor.fetchall()
        print(data_list)
        return data_list
    else:
        conn.commit()
        return '数据库语句执行成功'