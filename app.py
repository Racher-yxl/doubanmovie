import json
from flask import Flask,request,render_template,session,redirect
import re
from utils.query import querys  # 对抓取的HTML内容进行处理以获得需要的信息
from utils.homeData import *
from utils.timeData import *
from utils.rateData import *
from utils.addressData import *
from utils.typeData import *
from utils.tablesData import *
app = Flask(__name__)   # 声明一个Flask的类，__name__参数的作用是为了确定程序的根目录，以便获得静态文件的模板文件
app.secret_key = 'This is a app.secret_Key , You Know ?'



@app.route('/')
# app.route()是一个装饰器，它的作用就是把试图函数(可以简单的理解成就是它下面的函数)与某一个url(后面括号中的部分)绑定,当访问这个url时，就会运行这个视图函数
def every():
    return render_template('login.html')   # 后端核心代码，从数据库中计算所需数据，回传给前端
@app.route("/home")
def home():
    email = session['email']
    allData = getAllData()
    maxRate = getMaxRate()
    maxCast = getMaxCast()
    typesAll = getTypesAll()
    maxLang = getMaxLang()
    types = getType_t()   # 类型
    row,column = getRate_t()   # 评分
    tablelist = getTableList()
    return render_template(      # 后端核心代码，从数据库中计算所需数据，回传给前端
        "index.html",
        email=email,
        dataLen = len(allData),  # 统计电影数量
        maxRate=maxRate,  # 豆瓣最高评分
        maxCast=maxCast,  # 演员出场
        typeLen = len(typesAll),   # 类型个数
        maxLang = maxLang,  # 最多语言
        types=types,    # 类型
        row=list(row),
        column=list(column),
        tablelist=tablelist
    )

@app.route("/login",methods=['GET','POST'])
# methods指定请求这个url的方法，默认是get，这里指定使用get或post两种方式
def login():
    if request.method == 'POST':
        request.form = dict(request.form) # 如果请求方式为post，则在后台输出用户输入的信息。request可以获取到前端用户输入的信息，request.args获取get请求，request.form获取post请求

        def filter_fns(item):
            return request.form['email'] in item and request.form['password'] in item

        users = querys('select * from user', [], 'select')
        login_success = list(filter(filter_fns, users))
        if not len(login_success):
            return '账号或密码错误'

        session['email'] = request.form['email']
        return redirect('/home', 301)

    else:
        return render_template('./login.html')  # render_template对页面进行渲染，如果页面中存在待接受的参数，可将参数放在后面

@app.route("/registry",methods=['GET','POST'])
def registry():
    if request.method == 'POST':
        request.form = dict(request.form)
        if request.form['password'] != request.form['passwordCheked']:
            return '两次密码不符'
        else:
            def filter_fn(item):
                return request.form['email'] in item

            users = querys('select * from user', [], 'select')
            filter_list = list(filter(filter_fn, users))
            if len(filter_list):
                return '该用户名已被注册'
            else:
                querys('insert into user(email,password) values(%s,%s)',
                       [request.form['email'], request.form['password']])

        session['email'] = request.form['email']
        return redirect('/home', 301)

    else:
        return render_template('./register.html')

@app.route("/search/<int:searchId>",methods=['GET','POST'])
def search(searchId):
    email = session['email']
    allData = getAllData()
    data = []
    if request.method == 'GET':
        if searchId == 0:
            return render_template(
                'search.html',
                idData=data,
                email=email
            )

        for i in allData:
            if i[0] == searchId:
                data.append(i)
        return render_template(
                'search.html',
                data=data,
                email=email
            )
    else:
        searchWord = dict(request.form)['searchIpt']
        def filter_fn(item):
            if item[3].find(searchWord) == -1:
                return False
            else:
                return True
        data = list(filter(filter_fn,allData))
        return render_template(
            'search.html',
            data=data,
            email=email
        )

@app.route("/time_t",methods=['GET','POST'])
def time_t():
    email = session['email']
    row,column = getTimeList()
    moveTimeData = getMovieTimeList()
    return render_template(
        'time_t.html',
        email=email,
        row=list(row),
        column=list(column),
        moveTimeData=moveTimeData
    )

@app.route("/rate_t/<type>",methods=['GET','POST'])
def rate_t(type):
    email = session['email']
    typeAll = getTypesAll()
    rows,columns = getMean()
    if type == 'all':
        row, column = getRate_t()
    else:
        row,column = getRate_tType(type)
    if request.method == 'GET':
        starts,movieName = getStart('穆赫兰道')
    else:
        searchWord = dict(request.form)['searchIpt']
        starts,movieName = getStart(searchWord)
    return render_template(
        'rate_t.html',
        email=email,
        typeAll=typeAll,
        type=type,
        row=list(row),
        column=list(column),
        starts=starts,
        movieName=movieName,
        rows = rows,
        columns = columns
    )

@app.route("/address_t",methods=['GET','POST'])
def address_t():
    row,column = getAddressData()
    rows,columns = getLangData()
    return render_template('address_t.html',row=row,column=column,rows=rows,columns=columns)

@app.route('/type_t',methods=['GET','POST'])
def type_t():
    result = getMovieTypeData()
    return render_template('type_t.html',result=result)

@app.route("/movie/<int:id>")
def movie(id):
    allData = getAllData()
    idData = {}
    for i in allData:
        if i[0] == id:
            idData = i
    return render_template('movie.html',idData=idData)

@app.route('/tables/<int:id>')
def tables(id):
    if id == 0:
        tablelist = getTableList()
    else:
        deleteTableId(id)
        tablelist = getTableList()
    return render_template('tables.html',tablelist=tablelist)

@app.route('/title_c')
def title_c():
    return render_template('title_c.html')

@app.route('/summary_c')
def summary_c():
    return render_template('summary_c.html')

@app.route('/casts_c')
def casts_c():
    return render_template('casts_c.html')


@app.before_request
def before_requre():
    pat = re.compile(r'^/static')
    if re.search(pat,request.path):
        return
    if request.path == "/login" :
        return
    if request.path == '/registry':
        return
    uname = session.get('email')
    if uname:
        return None

    return redirect("/login")


if __name__ == '__main__':
    app.run()
