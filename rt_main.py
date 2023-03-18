import time

import gevent as gevent
import matplotlib.pyplot as plt
import baostock as bs
import pandas as pd
import random

import requests
import sqlalchemy
import cryptography
import pymysql

def stock_code(date_stock_code):
    lg = bs.login()
    # print('login respond error_code:'+lg.error_code)
    # print('login respond  error_msg:'+lg.error_msg)
    rs0 = bs.query_all_stock(day=date_stock_code)
    # print('query_all_stock respond error_code:'+rs.error_code)
    # print('query_all_stock respond  error_msg:'+rs.error_msg)
    stock_code_list = []
    while (rs0.error_code == '0') & rs0.next():  # 获取一条记录，将记录合并在一起
        stock_code_list.append(rs0.get_row_data())
    stock_code_result = pd.DataFrame(stock_code_list, columns=rs0.fields) #生成的有bj/sh/sz三个交易所
    stock_code_result = stock_code_result[~stock_code_result['code'].str.contains('bj')] #删除bj交易所数据
    stock_code_result = stock_code_result.reset_index(drop = True)
    bs.logout()
    print(stock_code_result)
    return stock_code_result


def stock_limitup(stock_code_result, date_stock_limitup):

    lg = bs.login()
    stock_limitup_pool = []
    stock_code_number = len(stock_code_result.index)

    for index, stock_limitup_code in stock_code_result.code.items():

        rs = bs.query_history_k_data(stock_limitup_code,'date,pctChg',
                                     start_date=date_stock_limitup, end_date=date_stock_limitup, frequency="d",adjustflag="3")

        data_list = []
        while (rs.error_code == '0') & rs.next():  # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
            stock_limitup_data = pd.DataFrame(data_list, columns=rs.fields)
            stock_limitup_data['pctChg'].replace('', 0, inplace=True) #处理所有股票的涨幅数据

        stock_limitup_number = len(stock_limitup_data.index)
        for i in range(stock_limitup_number):
            result1 = float(stock_limitup_data.loc[i].pctChg)
            print(result1)
            if result1 > 9:
               print('涨停代码'+stock_limitup_code,'涨停时间'+stock_limitup_data.loc[i].date,'增速为'+stock_limitup_data.loc[i].pctChg)
               stock_limitup_pool.append(stock_limitup_code)
        print(stock_limitup_pool)
    return stock_limitup_pool
#print(stock_limitup(stock_code('2022-06-30'), '2022-06-30'))

def trade_date(input_date,n):
 conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stocks', encoding='utf8')
 result = pd.read_sql('select * from stock_date',conn)
 a = result[(result.calendar_date == input_date)].index.tolist() #定位所输入的日期的位置
 b = result.loc[a].is_trading_day #输出0，1实际上为list
 c = a[0]  #a为索引，索引为list，去掉[] 注意必须要带0，否则在此报错
 b = b[c]  #输出0，1,此时b为str类型
 b = int(b)  #转换b
 if b == 1 :   #如果为交易日
     trade_day = input_date
 else: #不为交易日则输出最近的之前交易日
     while b == 0 :
         a = [v - 1 for v in a]
         b = result.loc[a].is_trading_day #计算b的值
         c = a[0] #这里三行不转换就会在上面的while报错
         b = b[c] #这里三行不转换就会在上面的while报错
         b = int(b) #这里三行不转换就会在上面的while报错
     trade_day =  result.loc[a].calendar_date[c]
 result1 = result[~result['is_trading_day'].str.contains('0')]  # 删除非交易日
 result1 = result1.reset_index(drop=True)                           #重新索引
 d = result1[(result1.calendar_date == trade_day)].index.tolist()#定位所输入的日期的位置
 e = [v + n for v in d]
 f = e[0]
 trade_day_end = result1.loc[e].calendar_date[f]
 print(trade_day_end)
 return trade_day_end

def random_figure():
 x_list = []
 y_list = []
 x = 0
 y = 0
 i = 0
 while i<1000000:
  y = y+random.uniform(-1.0,1.0)
  x = x+1
  i = i+1
  x_list.append(x)
  y_list.append(y)
 plt.plot(x_list,y_list)
 plt.show()
 return

def new_limit_up(date): #计算date前1天未涨停的所有股票
    new_limit_up_pool = []
    list0 = stock_limitup(stock_code(trade_date(date,-1)),trade_date(date,-1))
    list1 = stock_limitup(stock_code(trade_date(date,0)),trade_date(date,0))
    for i in list1:
        if i not in list0:
            new_limit_up_pool.append(i)
            print(i)
    return(new_limit_up_pool)

def low_price_value(list,date):
    lg = bs.login()
    low_price_value_pool = []
    for i in list:
     rs = bs.query_history_k_data_plus(i,
                                      "close,volume,turn",
                                      start_date=trade_date(date, 0), end_date=trade_date(date, 0),
                                      frequency="d", adjustflag="3")  # frequency="d"取日k线，adjustflag="3"默认不复权
     data_list = []
     while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
     result = pd.DataFrame(data_list, columns=rs.fields)
     price = float(result.close)
     all_stock = int(result.volume)/float(result.turn)
     value = all_stock*price
     if value < 6000000000:
        if price < 6:
            low_price_value_pool.append(i)
     return low_price_value_pool

def get_date_data(code,start_date,end_date): #获得目标股票的涨跌幅等数据
    lg = bs.login()
    rs = bs.query_history_k_data_plus(code,
    "date,code,open,high,low,close,preclose,volume,amount,adjustflag,turn,tradestatus,pctChg,isST",
    start_date=start_date, end_date=end_date,
    frequency="d", adjustflag="3")
    data_list = []
    while (rs.error_code == '0') & rs.next():
     data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    return result

#print(get_date_data('sz.002526','2020-09-09','2022-07-08'))
def get_stock_basic_date(code):   #该函数可以获得名称code_name，上市日期ipoDate，退市日期outDate，证券类型type，上市状态status
    lg = bs.login()
    rs = bs.query_stock_basic(code=code)
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    return result
#print(get_stock_basic_date('sh.000001').ipoDate[0]) #注意.访问的结果为一个list，要变为str需要后面加上index

def c_trade_date(date,n): #连续前n天的交易日
 list = range(0,n,1)
 A = []
 for i in list:
     A.append((date,-i))
 jobs = [

 gevent.spawn(trade_date, *a) for a in A




 ]
 gevent.joinall(jobs)
 result = [job.value for job in jobs]
 return result

#print(c_trade_date('2022-07-09',10))


def MA5(code,date):
    result = get_date_data(code, trade_date(date,-4), trade_date(date,0))
    list = range(0,5,1)
    A= [None] * 5   #使用一个列表来避免使用动态的变量名，A[i]就代表向前的i天
    B = [None] * 5
    C = [None] * 5
    sumall = 0
    for i in list:
     A[i]=trade_date(date,-i)
     B[i] = result[(result.date == A[i])].index.tolist()  # 定位所输入的日期的位置,i5即为index
     C[i] = result.loc[B[i]].close #使用.定位后输出list
     C[i] = C[i].reset_index(drop=True)  # 重新索引
     C[i] = C[i][0]
     C[i] = float(C[i])
     sumall += C[i]
    ma5 = sumall/5
    return ma5
#print(MA5('sz.002526','2022-07-07'))

def MA10(code,date):
    result = get_date_data(code, trade_date(date,-9), trade_date(date,0))
    list = range(0,10,1)
    A = [None] * 10  # 使用一个列表来避免使用动态的变量名，A[i]就代表向前的i天
    B = [None] * 10
    C = [None] * 10
    sumall = 0
    for i in list:
        A[i] = trade_date(date, -i)
        B[i] = result[(result.date == A[i])].index.tolist()  # 定位所输入的日期的位置,i5即为index
        C[i] = result.loc[B[i]].close  # 使用.定位后输出list
        C[i] = C[i].reset_index(drop=True)  # 重新索引
        C[i] = C[i][0]
        C[i] = float(C[i])
        print(C[i])
        sumall += C[i]
    ma10 = sumall / 10
    return ma10
#print(MA10('sz.002526','2022-07-08'))
def MA20(code,date):
    result = get_date_data(code, trade_date(date,-19), trade_date(date,0))
    list = range(0,20,1)
    A = [None] * 20  # 使用一个列表来避免使用动态的变量名，A[i]就代表向前的i天
    B = [None] * 20
    C = [None] * 20
    sumall = 0
    #A =  c_trade_date(date,20)
    for i in list:
        A[i] = trade_date(date, -i)
        B[i] = result[(result.date == A[i])].index.tolist()  # 定位所输入的日期的位置,i5即为index
        C[i] = result.loc[B[i]].close  # 使用.定位后输出list
        C[i] = C[i].reset_index(drop=True)  # 重新索引
        C[i] = C[i][0]
        C[i] = float(C[i])
        print(C[i])
        sumall += C[i]
    ma20 = sumall / 20
    return ma20
#
# r_data = get_date_data('sz.002526','2022-05-01','2022-07-10')
# for index,date in r_data.date.items():
#    r_data.loc[index,'MA5']= MA5('sz.002526',date)
# for index,date in r_data.date.items():
#    r_data.loc[index,'MA20']= MA20('sz.002526',date)
# plt.rcParams['font.sans-serif']=['SimHei']
# colors=['black', 'red', 'green']
# plt.gca().set_prop_cycle(color=colors)
# r_data[['close','MA5','MAA20']]=r_data[['close','MA5','MA20']].astype('float')
# r_data.plot(x='date',y=['close','MA5','MA20'])
# plt.title("山东矿机",fontsize=15)
# plt.xlabel("时间",fontsize=13)
# plt.ylabel("价格",fontsize=13)
# plt.legend()
# plt.show()

def limit_up_point(date):
 list1 = stock_limitup(stock_code(trade_date(date,-1)),trade_date(date,-1))
 list2 = stock_limitup(list1,trade_date(date,0))
 number1 = len(list1)
 number2 = len(list2)
 point = number2/number1
 print(point)
 return point

def input_database(): #单次使用过的函数 #2022.7.14更新
 list0 = stock_code('2022-07-13')
 print(list0)
 for index,code in list0.code.items():
     print(code+'_d')
     lg = bs.login()
     rs = bs.query_history_k_data_plus(code,
                                       "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg",
                                       start_date='2015-01-01', end_date='2022-07-13',
                                       frequency="d", adjustflag="3")
     data_list = []
     while (rs.error_code == '0') & rs.next():
         data_list.append(rs.get_row_data())
     result = pd.DataFrame(data_list, columns=rs.fields)
     print(result)
     conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stocks',encoding='utf8')
     pd.io.sql.to_sql(result,code+'d',conn,if_exists = 'replace')
 return


#input_database()
def getTick(code):
    url = 'http://hq.sinajs.cn/list='+code
    headers={'Referer':'https://fiance.sina.com.cn/'}
    page = requests.get(url,headers=headers)
    stock_info = page.text
    print(stock_info)
    mt_info = stock_info.split(',')
    last = float(mt_info[1])
    trade_datetime = mt_info[30]+''+mt_info[31]
    tick = (last,trade_datetime)
    return tick
#last_tick = getTick('sh600519')
#print(last_tick)

