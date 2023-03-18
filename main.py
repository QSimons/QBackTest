import copy
import inspect
import os
import time
import datetime
import matplotlib.pyplot as plt
import baostock as bs
import numpy as np
import pandas as pd
import random
import sqlalchemy
import akshare as ak
import pymysql
import seaborn as sns
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
    stock_code_result = pd.DataFrame(stock_code_list, columns=rs0.fields)  # 生成的有bj/sh/sz三个交易所
    stock_code_result = stock_code_result[~stock_code_result['code'].str.contains('bj')]  # 删除bj交易所数据
    stock_code_result = stock_code_result.reset_index(drop=True)
    bs.logout()
    print(stock_code_result)
    return stock_code_result

def datatbase_stock_code_list(target = 'stocks_b'):
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database=target
    )
    cursor = db.cursor()
    sql = 'SHOW TABLES FROM STOCKS'
    cursor.execute(sql)
    result = cursor.fetchall()
    result = list(result)
    for i in range(0, len(result)):
        result[i] = ''.join(result[i])
        result[i] = result[i][:-1]
    return result

def stock_limitup(stock_code_result, date_stock_limitup):
    lg = bs.login()
    stock_limitup_pool = []
    stock_code_number = len(stock_code_result.index)

    for index, stock_limitup_code in stock_code_result.code.items():

        rs = bs.query_history_k_data(stock_limitup_code, 'date,pctChg',
                                     start_date=date_stock_limitup, end_date=date_stock_limitup, frequency="d",
                                     adjustflag="3")

        data_list = []
        while (rs.error_code == '0') & rs.next():  # 获取一条记录，将记录合并在一起
            data_list.append(rs.get_row_data())
            stock_limitup_data = pd.DataFrame(data_list, columns=rs.fields)
            stock_limitup_data['pctChg'].replace('', 0, inplace=True)  # 处理所有股票的涨幅数据

        stock_limitup_number = len(stock_limitup_data.index)
        for i in range(stock_limitup_number):
            result1 = float(stock_limitup_data.loc[i].pctChg)
            print(result1)
            if result1 > 9:
                print('涨停代码' + stock_limitup_code, '涨停时间' + stock_limitup_data.loc[i].date,
                      '增速为' + stock_limitup_data.loc[i].pctChg)
                stock_limitup_pool.append(stock_limitup_code)
        print(stock_limitup_pool)
    return stock_limitup_pool


# print(stock_limitup(stock_code('2022-06-30'), '2022-06-30'))

def trade_date(input_date, n):
    conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stocks', encoding='utf8')
    result = pd.read_sql('select * from stock_date', conn)
    a = result[(result.calendar_date == input_date)].index.tolist()  # 定位所输入的日期的位置
    b = result.loc[a].is_trading_day  # 输出0，1实际上为list
    c = a[0]  # a为索引，索引为list，去掉[] 注意必须要带0，否则在此报错
    b = b[c]  # 输出0，1,此时b为str类型
    b = int(b)  # 转换b
    if b == 1:  # 如果为交易日
        trade_day = input_date
    else:  # 不为交易日则输出最近的之前交易日
        while b == 0:
            a = [v - 1 for v in a]
            b = result.loc[a].is_trading_day  # 计算b的值
            c = a[0]  # 这里三行不转换就会在上面的while报错
            b = b[c]  # 这里三行不转换就会在上面的while报错
            b = int(b)  # 这里三行不转换就会在上面的while报错
        trade_day = result.loc[a].calendar_date[c]
    result1 = result[~result['is_trading_day'].str.contains('0')]  # 删除非交易日
    result1 = result1.reset_index(drop=True)  # 重新索引
    d = result1[(result1.calendar_date == trade_day)].index.tolist()  # 定位所输入的日期的位置
    e = [v + n for v in d]
    f = e[0]
    trade_day_end = result1.loc[e].calendar_date[f]
    return trade_day_end


def get_trade_day_list():
    conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stocks', encoding='utf8')
    trade_date_list = pd.read_sql('select * from stock_date', conn)
    trade_date_list = trade_date_list[~trade_date_list['is_trading_day'].str.contains('0')]  # 删除非交易日
    trade_date_list = trade_date_list.reset_index(drop=True)  # 重新索引
    trade_date_list = trade_date_list['calendar_date'].tolist()
    return trade_date_list


# print(get_trade_day_list())



def get_stock_basic_data(code):  # 该函数可以获得名称code_name，上市日期ipoDate，退市日期outDate，证券类型type，上市状态status
    lg = bs.login()
    rs = bs.query_stock_basic(code=code)
    data_list = []
    while (rs.error_code == '0') & rs.next():
        data_list.append(rs.get_row_data())
    result = pd.DataFrame(data_list, columns=rs.fields)
    return result

def database_stock_basic_data(code):
    code = '`'+code+'`'
    conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stock_basic_data', encoding='utf8')
    result = pd.read_sql('select * from %s' % code, conn)  # 传参时必须使用转义符
    print(result)
    return result
#database_stock_basic_data('sh.601298')


def get_date_data(code, start_date, end_date):  # 获得目标股票的涨跌幅等数据
    conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stocks_b', encoding='utf8')
    m = '`' + code + 'd' + '`'  # code中含有特殊字符.需要使用引号来指代
    result = pd.read_sql('select * from %s' % m, conn)  # 传参时必须使用转义符
    first_line = result.head(1)
    first_date = first_line.loc[0,'date']

    timeArray_s = time.strptime(start_date, "%Y-%m-%d")  # 比较开始日期和数据开始日期
    timeStamp_s = int(time.mktime(timeArray_s))
    timeArray_f = time.strptime(first_date, "%Y-%m-%d")
    timeStamp_f = int(time.mktime(timeArray_f))
    if timeStamp_s < timeStamp_f:
        print('回测开始时间小于数据开始日期%s，已经将开始日期调整到开始日期30个交易日后（防止均线错误）' % first_date)
        start_date = trade_date(first_date, 30)
    start_date = trade_date(start_date, 0)
    end_date = trade_date(end_date, 0)
    a = result[(result.date == start_date)].index.tolist()  # 定位所输入的日期的位置
    b = result[(result.date == end_date)].index.tolist()  # 定位所输入的日期的位置
    a = int(a[0])  # 转换为int
    b = int(b[0])
    result1 = result.iloc[a:b + 1]
    result1 = result1.reset_index(drop=True)
    result1 = result1.drop(columns='index')
    return result1







#print(get_stock_basic_date('sz.002526')) #注意.访问的结果为一个list，要变为str需要后面加上index

class technical_indicators():   #data指输入日线数据，输出的有空值！！
    def __init__(self,data):
        self.data = data
        self.data[['open','high','low','close','pctChg']] = self.data[['open','high','low','close','pctChg']].astype('float')

    def MA5(self):
        self.data['MA5'] = self.data['close'].rolling(window = 5).mean()
        return self


    def MA10(self):
        self.data['MA10'] = self.data['close'].rolling(window= 10).mean()
        return self


    def MA20(self):
        self.data['MA20'] = self.data['close'].rolling(window= 20).mean()
        return self

    def RSRS(self):
        for i in range(17, self.data.tail(1).index[0] + 1):
            print(self.data[i - 17:i]['low'].tolist())
            low_list = self.data[i - 17:i]['low'].tolist()
            high_list = self.data[i - 17:i]['high'].tolist()
            k, b = np.polyfit(low_list, high_list, deg=1)
            self.data.loc[i, 'RSRS'] = k
        return self

    def KDJ(self,n = 9,K0 = 50,D0 = 50):
        temp_data = self.data
        temp_data['Ln'] = temp_data['low'].rolling(window = n).min()
        temp_data['Hn'] = temp_data['high'].rolling(window = n).max()
        i = 0 #用于标记，第一次要将KDJ值标记为初始量
        for index in temp_data.index.tolist():
            print(pd.isnull(temp_data.loc[index,'Ln']))
            if (pd.isnull(temp_data.loc[index,'Ln']) or pd.isnull(temp_data.loc[index,'Hn'])): #判断是否为空，为空则不进行计算
                pass
            else:
                print(index)
                self.data.loc[index,'RSV'] = (temp_data.loc[index,'close']-temp_data.loc[index,'Ln'])/(temp_data.loc[index,'Hn']-temp_data.loc[index,'Ln'])
                if (i==0):
                    self.data.loc[index,'K'] = K0
                    self.data.loc[index,'D'] = D0
                    self.data.loc[index,'J'] = 3*K0 - 2*D0
                    i = i +1
                else:
                    self.data.loc[index,'K'] = (2 * self.data.loc[index-1,'K'])/3 + (self.data.loc[index,'RSV'])/3
                    self.data.loc[index, 'D'] = (2 * self.data.loc[index-1,'D'])/3 + (self.data.loc[index,'K'])/3
                    self.data.loc[index, 'J'] = 3*self.data.loc[index,'K'] - 2*self.data.loc[index, 'D']
        return self

    def dMA20(self):
        d = 0.01
        n = 1.0

        n_list = []
        result_list = []
        for i in range(0,2* int(n/d)):
            n = n - d
            self.data['MA10'] = self.data['close'].rolling(window=20).mean()
            self.data['dMA10'] = self.data['MA10'].pct_change()
            print(self.data[(self.data['dMA10']>n)]['pctChg'].mean())
            result = self.data[(self.data['dMA10']>n)]['pctChg'].mean() * len(self.data[(self.data['dMA10']>n)])
            result_list.append(result)
            n_list.append(n)
            plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置输出中文
            plt.rcParams['axes.unicode_minus'] = False  # 避免负数无法输出
            # plt.rcParams['figure.figsize'] = (19.2, 10.8)
            # plt.figure(dpi=100)
            plt.plot(n_list,result_list)
            plt.show()






    def get_result(self):  #前面的可以自选来链式进行函数，结果从这里输出
        return self.data

#technical_indicators(get_date_data('sz.002526','2022-02-01','2022-08-01')).dMA20()




class stock_backtest():
    def __init__(self,code,start_date,end_date,b_date,s_date,fee=0.03,risk_control = True):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.b_date = b_date
        self.s_date = s_date
        self.fee = fee
        self.mark = inspect.getframeinfo(inspect.currentframe().f_back)[2]
        self.risk_control = risk_control
        # self.start_date = stock_backtest.handle_backtest_starttime(self)
        # self.b_index = stock_backtest.handle_trade_day_index(self)[0]
        # self.s_index = stock_backtest.handle_trade_day_index(self)[1]
        # self.data = stock_backtest.handle_backtest(self)[0]
        # stock_backtest.output_backtest()

    def handle_backtest_starttime(self):  # 此函数比较开始回测日期和ipo日期来防止崩溃
        timeArray_s = time.strptime(self.start_date, "%Y-%m-%d")  # 比较开始日期和ipo日期
        timeStamp_s = int(time.mktime(timeArray_s))
        timeArray_i = time.strptime(get_stock_basic_data(self.code).iat[0, 2], "%Y-%m-%d")
        timeStamp_i = int(time.mktime(timeArray_i))
        print('上市日期%s' % get_stock_basic_data(self.code).iat[0, 2])
        if timeStamp_s < timeStamp_i:
            print('回测开始时间小于上市日期%s，已经将开始日期调整到上市30个交易日后（防止均线错误）' % get_stock_basic_data(self.code).iat[0, 2])
            self.start_date = trade_date(get_stock_basic_data(self.code).iat[0, 2], 30)
        self.data = get_date_data(self.code,self.start_date,self.end_date)
        self.data[['close', 'open', 'high','low','volume']] = self.data[['close', 'open', 'high','low','volume']].astype('float')
        return self


    def buy_check(self,b_index): #检查买入信号发生后一天能否买入
        if (b_index[-1] == self.data.tail(1).index[0]):
            del b_index[-1]
        else:
            for i in b_index:
                today_close = self.data.loc[i,'close']
                tomorrow_open = self.data.loc[i+1,'open']
                tomorrow_open_max = round(today_close*1.1,2)
                if (tomorrow_open >= tomorrow_open_max):
                    b_index.remove(i)
                    print('%s 在 %s 发生开盘涨停，无法买入'%(self.code,self.data.loc[i+1,'date']))
                if (self.data.loc[i+1,'volume']==0):
                    b_index.remove(i)
                    print('%s 在 %s 发生停牌，无法买入'%(self.code,self.data.loc[i+1,'date']))
        return b_index
    def sell_check(self,s_index):
        if (s_index[-1] == self.data.tail(1).index[0]):
            del s_index[-1]
        else:
            for i in s_index:
                today_close = self.data.loc[i, 'close']
                tomorrow_close = self.data.loc[i + 1, 'close']
                tomorrow_close_min = round(today_close * 0.9, 2)
                if (tomorrow_close_min >= tomorrow_close):
                    s_index.remove(i)
                    print('%s 在 %s 发生尾盘跌停，无法卖出' %(self.code, self.data.loc[i+1, 'date']))
                if (self.data.loc[i+1,'volume']==0):
                    s_index.remove(i)
                    print('%s 在 %s 发生停牌，无法卖出'%(self.code,self.data.loc[i+1,'date']))
        return s_index
    def risk_control(self,b_index,s_index):
    #跌破十日最低价后停止买入，并且立即平仓
        self.data['risk_line'] = self.data['low'].rolling(window = 10).min()
        self.data['risk_line'].fillna(0,inplace = True)
        for b in b_index:
            if (self.data.loc[b,'close'] <= self.data.loc[b,'risk_line']):
                b_index.remove(b)
        emergency_sell_index = self.data.loc[(self.data['close']<=self.data['risk_line'] )].index.tolist()
        s_index = s_index + emergency_sell_index
        s_index.sort()#如果不重新排序则进入sell_check的时候不一定将最大的检测出来
        return [b_index,s_index]
    def handle_trade_day_index(self): #更新日志1.已完成列表+1的功能，2.已经将回测程序输入的值变更为date
        b_index = []
        s_index = []
        print('买入信号发生时间为 %s '%(self.b_date))
        print('卖出信号发生时间为 %s '%(self.s_date))
        [b_index.append(self.data.loc[(self.data['date']==i)].index[0]) for i in self.b_date]    #index后加个[0]可以将index的数据类型变为int
        [s_index.append(self.data.loc[(self.data['date'] == i)].index[0]) for i in self.s_date]     #这里将全部的日期换为index，这样以后调用时就都统一到一张df上面
        if (self.risk_control == True):
            b_index,s_index =stock_backtest.risk_control(self,b_index,s_index)
        else:
            pass
        b_index = stock_backtest.buy_check(self,b_index)
        s_index = stock_backtest.sell_check(self,s_index)
        b_s_list = b_index + s_index
        b_s_list.sort()
        start = b_index[0]
        start_index_in_bs = b_s_list.index(start)
        f_buy_index_list = [start]
        f_sell_index_list = []
        b_s_list =b_s_list[start_index_in_bs+1:] #b_s表更新，第一个从卖开始


        k = 0
        for i in b_s_list:
            if (k%2 == 0):
                if (i in b_index):
                    pass
                else:
                    f_sell_index_list.append(i)
                    k = k + 1
            else:
                if (i in b_index):
                    f_buy_index_list.append(i)
                    k = k + 1
                else:
                    pass
        if (f_sell_index_list[-1] < f_buy_index_list[-1]):
            f_buy_index_list = f_buy_index_list[:-1]
        else:
            pass
        f_buy_index_list = [i+1 for i in f_buy_index_list]
        f_sell_index_list = [i+1 for i in f_sell_index_list]
        # if (f_sell_index_list[-1]>=len(self.data)): #这个是为了解决当最后一日出现卖出信号时导致超出index范围的bug
        #     del(f_buy_index_list[-1])
        #     del(f_sell_index_list[-1])
        self.b_index = f_buy_index_list
        self.s_index = f_sell_index_list

        return self
    def do_buy_day(self,index):
        self.property = self.property - self.data.loc[index,'open'] + self.data.loc[index,'close']
        self.cash = self.cash - self.data.loc[index,'open']
        self.data.loc[index,'property'] = self.property
        self.data.loc[index,'cash'] = self.cash
        self.property_list.append(self.property)
        self.cash_list.append(self.cash)
        print('已在 %s 进行了买入操作'%(self.data.loc[index,'date']))
        return self
    def do_sell_day(self,index):
        self.property = self.property - self.data.loc[index-1,'close'] + self.data.loc[index,'close'] - self.fee
        self.cash = self.cash + self.data.loc[index,'close'] - self.fee
        self.data.loc[index,'property'] = self.property
        self.data.loc[index,'cash'] = self.cash
        self.property_list.append(self.property)
        self.cash_list.append(self.cash)
        print('已在 %s 进行了卖出操作'%(self.data.loc[index,'date']))
        return self
    def full_condition(self,index):
        self.property = self.property - self.data.loc[index - 1, 'close'] + self.data.loc[index, 'close']
        self.data.loc[index,'property'] = self.property
        self.data.loc[index,'cash'] = self.cash
        return self
    def empty_condition(self,index):
        self.data.loc[index, 'property'] = self.property
        self.data.loc[index, 'cash'] = self.cash
        return self

    def initial_backtest(self):
        #必须初始化数据类型
        self.data[['open', 'close']] = self.data[['open', 'close']].astype('float')
        #裁剪df使得其从第一次买入开始,到最后一次卖出结束
        self.data = self.data[self.b_index[0]:self.s_index[-1] +1]
        #初始化统计量
        self.property_list = []
        self.cash_list = []
        self.property = self.data.loc[self.b_index[0], 'open']
        self.cash = self.data.loc[self.b_index[0], 'open']

    def handle_backtest(self):
        stock_backtest.initial_backtest(self)
        b_to_s_dict = dict(zip(self.b_index,self.s_index))
        full_list = []
        for b, s in b_to_s_dict.items():
             list_temp = list(range(b+1,s)) #range和list类型不能相加，必须转换后才能相加
             full_list = full_list + list_temp
        for index in self.data.index.values:
            if index in self.b_index:
                stock_backtest.do_buy_day(self,index)
            elif index in self.s_index:
                stock_backtest.do_sell_day(self,index)
            elif index in full_list:
                stock_backtest.full_condition(self,index)
            else:
                stock_backtest.empty_condition(self,index)

        return self




    def output_backtest(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置输出中文
        plt.rcParams['axes.unicode_minus'] = False  # 避免负数无法输出
        plt.rcParams['figure.figsize'] = (19.2, 10.8)
        plt.figure(dpi=1000)
        self.data.plot(x='date', y=['close', 'property'])
        stock_name = get_stock_basic_data(self.code).iat[0, 1]
        plt.title(stock_name + '回测模型', fontsize=15)
        plt.xlabel("时间", fontsize=13)
        plt.ylabel("权益", fontsize=13)
        #注意如果建立了新的策略就需要在backtest文件夹下放入策略函数相应名字的文件夹来存储数据
        plt.savefig('D:/python_test/backtest/%s/backtest_%s_%s-%s.svg' % (self.mark,stock_name, self.start_date, self.end_date))
        plt.legend()
        plt.show()
        self.data.to_csv('D:/python_test/backtest/%s/backtest_%s_%s-%s.csv' % (self.mark,stock_name, self.start_date, self.end_date), index=True, encoding='utf-8_sig')





# double_average('sh.000001','2022-04-01','2022-07-28')





class company_finance:
    def __init__(self, code, year, quarter,function):  # 键盘输入的数字为str类型，下方list为int类型如果不转换则dataframe筛选失败
        if (function == 'y'):    #y为同比q为环比，默认为y
            i = 4
        elif (function == 'q'):
            i = 1
        else:
            i = 4

        year = int(year)
        quarter = int(quarter)

        list_year = [2017] * 4 + [2018] * 4 + [2019] * 4 + [2020] * 4 + [2021] * 4 + [2022] * 4
        list_quarter = [1, 2, 3, 4] * 6
        list_date = {'year': list_year, 'quarter': list_quarter}
        df_date = pd.DataFrame(list_date)

        input_date_index = df_date.loc[(df_date['year'] == year) & (df_date['quarter'] == quarter)].index.tolist()[0]
        last_date_index = input_date_index - i  # 可通过这个来调整同比环比，同比4环比1

        self.code = code
        self.year = year
        self.quarter = quarter
        self.l_year = df_date.loc[last_date_index, 'year']
        self.l_quarter = df_date.loc[last_date_index, 'quarter']

    def finance_cash(self, year, quarter):  # 现金
        lg = bs.login()
        # 季频现金流量
        cash_flow_list = []
        rs_cash_flow = bs.query_cash_flow_data(code=self.code, year=year, quarter=quarter)
        while (rs_cash_flow.error_code == '0') & rs_cash_flow.next():
            cash_flow_list.append(rs_cash_flow.get_row_data())
        result_cash_flow = pd.DataFrame(cash_flow_list, columns=rs_cash_flow.fields)
        return result_cash_flow

    def finance_profit(self, year, quarter):
        lg = bs.login()
        # 查询季频估值指标盈利能力
        profit_list = []
        rs_profit = bs.query_profit_data(code=self.code, year=year, quarter=quarter)
        while (rs_profit.error_code == '0') & rs_profit.next():
            profit_list.append(rs_profit.get_row_data())
        result_profit = pd.DataFrame(profit_list, columns=rs_profit.fields)
        return result_profit

    def finance_dupont(self, year, quarter):
        lg = bs.login()
        # 查询杜邦指数
        dupont_list = []
        rs_dupont = bs.query_dupont_data(code=self.code, year=year, quarter=quarter)
        while (rs_dupont.error_code == '0') & rs_dupont.next():
            dupont_list.append(rs_dupont.get_row_data())
        result_dupont = pd.DataFrame(dupont_list, columns=rs_dupont.fields)
        return result_dupont

    def roeAvg_F_score_1_2(self):
        result_profit = company_finance.finance_profit(self, self.year, self.quarter)
        roeAvg = result_profit.loc[0, 'roeAvg']
        if roeAvg == '':
            roeAvg_F_score = 0.5
            d_roeAvg_F_score = 0.5
            handle_num = 2
        else:

            handle_num = 0
            roeAvg = float(roeAvg)
            if roeAvg > 0:
                roeAvg_F_score = 1
            else:
                roeAvg_F_score = 0
            l_result_profit = company_finance.finance_profit(self, self.l_year, self.l_quarter)
            l_result_profit['roeAvg'] = l_result_profit['roeAvg'].astype(float)
            l_roeAvg = l_result_profit.loc[0, 'roeAvg']
            d_roeAvg = roeAvg - l_roeAvg
            if d_roeAvg > 0:
                d_roeAvg_F_score = 1
            else:
                d_roeAvg_F_score = 0
        result = [roeAvg_F_score, d_roeAvg_F_score, handle_num]
        return result

    def CRS_F_score_1_2(self):  # 经营活动产生的现金流量净额与营业收入之比大于0，反映现金流量为正
        result_cash = company_finance.finance_cash(self, self.year, self.quarter)
        cash_flow = result_cash.loc[0, 'CFOToNP']
        if cash_flow == '':
            cash_flow_F_score = 0.5
            d_cash_flow_F_score = 0.5
            handle_num = 2
        else:
            handle_num = 0
            cash_flow = float(cash_flow)
            if cash_flow > 0:
                cash_flow_F_score = 1
            else:
                cash_flow_F_score = 0
            l_result_cash = company_finance.finance_cash(self, self.l_year, self.l_quarter)
            l_result_cash['CFOToNP'] = l_result_cash['CFOToNP'].astype(float)
            l_cash_flow = l_result_cash.loc[0, 'CFOToNP']
            d_cash_flow = cash_flow - l_cash_flow
            if d_cash_flow > 0:
                d_cash_flow_F_score = 1
            else:
                d_cash_flow_F_score = 0
        result = [cash_flow_F_score, d_cash_flow_F_score, handle_num]
        return result

    def dLEVER_F_score(self):
        result_dupont = company_finance.finance_dupont(self, self.year, self.quarter)
        lever = result_dupont.loc[0, 'dupontAssetStoEquity']
        if lever == '':
            dLEVER_F_score = 0.5
            handle_num = 1
        else:
            handle_num = 0
            lever = float(lever)
            l_result_dupont = company_finance.finance_dupont(self, self.l_year, self.l_quarter)
            l_result_dupont['dupontAssetStoEquity'] = l_result_dupont['dupontAssetStoEquity'].astype(float)
            l_lever = l_result_dupont.loc[0, 'dupontAssetStoEquity']
            d_lever = lever - l_lever
            if d_lever < 0:
                dLEVER_F_score = 1
            else:
                dLEVER_F_score = 0
        result = [dLEVER_F_score, handle_num]
        return result

    def dLIQUID_F_score(self):
        result_cash = company_finance.finance_cash(self, self.year, self.quarter)
        CAToAsset = result_cash.loc[0, 'CAToAsset']
        if CAToAsset == '':
            dLIQUID_F_score = 0.5
            handle_num = 1
        else:
            handle_num = 0
            CAToAsset = float(CAToAsset)
            l_result_cash = company_finance.finance_cash(self, self.l_year, self.l_quarter)
            l_result_cash['CAToAsset'] = l_result_cash['CAToAsset'].astype(float)
            l_CAToAsset = l_result_cash.loc[0, 'CAToAsset']
            dliquid = CAToAsset - l_CAToAsset
            if dliquid > 0:
                dLIQUID_F_score = 1
            else:
                dLIQUID_F_score = 0
        result = [dLIQUID_F_score,handle_num]
        return result

    def dMARGIN_F_score(self):
        result_profit = company_finance.finance_profit(self, self.year, self.quarter)
        gpMargin = result_profit.loc[0, 'gpMargin']
        if gpMargin == '':
            dMARGIN_F_score = 0.5
            handle_num = 1
        else:
            handle_num = 0
            gpMargin = float(gpMargin)
            l_result_profit = company_finance.finance_profit(self, self.l_year, self.l_quarter)
            l_result_profit['gpMargin'] = l_result_profit['gpMargin'].astype(float)
            l_gpMargin = l_result_profit.loc[0, 'gpMargin']
            dmargin = gpMargin - l_gpMargin
            if dmargin > 0:
                dMARGIN_F_score = 1
            else:
                dMARGIN_F_score = 0
        result = [dMARGIN_F_score,handle_num]
        return result

    def dTURN_F_score(self):
        result_dupont = company_finance.finance_dupont(self, self.year, self.quarter)
        turn = result_dupont.loc[0, 'dupontAssetTurn']
        if turn == '':
            dTURN_F_score = 0.5
            handle_num =  1
        else:
            handle_num = 0
            turn = float(turn)
            l_result_dupont = company_finance.finance_dupont(self, self.l_year, self.l_quarter)
            l_result_dupont['dupontAssetTurn'] = l_result_dupont['dupontAssetTurn'].astype(float)
            l_turn = l_result_dupont.loc[0, 'dupontAssetTurn']
            dturn = turn - l_turn
            if dturn > 0:
                dTURN_F_score = 1
            else:
                dTURN_F_score = 0
        result = [dTURN_F_score,handle_num]
        return result

    def F_score(self):

        roeAvg_F_score = company_finance.roeAvg_F_score_1_2(self)[0]
        droeAvg_F_score = company_finance.roeAvg_F_score_1_2(self)[1]
        CRS_F_score = company_finance.CRS_F_score_1_2(self)[0]
        dCRS_F_score = company_finance.CRS_F_score_1_2(self)[1]

        dLEVER_F_score = company_finance.dLEVER_F_score(self)[0]
        dLIQUID_F_score = company_finance.dLIQUID_F_score(self)[0]
        dMARGIN_F_score = company_finance.dMARGIN_F_score(self)[0]
        dTURN_F_score = company_finance.dTURN_F_score(self)[0]
        F_score = roeAvg_F_score + droeAvg_F_score + CRS_F_score + dCRS_F_score + dLEVER_F_score + dLIQUID_F_score + dMARGIN_F_score + dTURN_F_score
        handle_num = company_finance.roeAvg_F_score_1_2(self)[2] + company_finance.CRS_F_score_1_2(self)[2] + company_finance.dLEVER_F_score(self)[1] + company_finance.dLIQUID_F_score(self)[1] + company_finance.dMARGIN_F_score(self)[1] + company_finance.dTURN_F_score(self)[1]

        result = [F_score,handle_num]
        return result


def start_F_score_choose(year, quarter,function):  # 已经默认设置为环比1quarter
    if (function == 'y'):
        name = '同比'
    elif(function == 'q'):
        name = '环比'
    else:
        name = '同比'

    i = 0
    today = datetime.date.today()
    now_stock = main.stock_code(main.trade_date(str(today), -1))  # 导入包时要import datetime 否则会报错:attribute error
    now_stock_list = now_stock['code'].tolist()  # .tolist()可以将只有一列的dataframe转化为list
    temp_df = pd.DataFrame(columns=['stock_code', 'stock_name', 'F_score', 'handle_num', 'price'])
    df = pd.DataFrame(columns=['stock_code', 'stock_name', 'F_score', 'handle_num', 'price'])
    result_frame = pd.DataFrame(columns=['stock_code', 'stock_name', 'F_score', 'handle_num', 'price'])

    if(os.path.isfile('D:\\F-SCORE-temp.csv')):
         temp_df = pd.read_csv("D:\\F-SCORE-temp.csv")
         df = temp_df
         last_df = temp_df.tail(1)
         last_df = last_df.reset_index(drop=True)
         last_code = last_df.loc[0,'stock_code']
         last_code_index = now_stock_list.index(last_code)
         now_stock_list = now_stock_list[last_code_index+1: ]
         print('已读取缓存，从 %s 开始'%(last_code))
    else:
         print('无缓存可以读取')
    for stock_code in now_stock_list:
        try:
              result_frame = result_frame.drop(index=result_frame.index)

              F_score = company_finance(stock_code, year, quarter,function= function).F_score()[0]
              handle_num = company_finance(stock_code, year, quarter,function = function).F_score()[1]
              stock_price = get_date_data(stock_code,'2022-08-11','2022-08-11').loc[0,'close']
              stock_name = main.get_stock_basic_data(stock_code).iat[0, 1]
              print('正在处理   %s'%(stock_name))
              i = i + 1
              data_list = [stock_code, stock_name, F_score,handle_num,stock_price]
              result_frame.loc[0] = data_list
              frames = [df,result_frame]
              df = pd.concat(frames)
              df = df.reset_index(drop=True)

              print(df)
              if(i%3 == 0):
                  df.to_csv("D:\\F-SCORE-temp.csv", index=False,encoding='utf-8_sig')
        except Exception as e:
              print('无法获得财务数据',e)
    df = df.sort_values(by='F_score', ascending=False)  # 这里可以更改数据的排序方式！！！！
    df.to_csv("D:\\F-SCORE(%s-%s)-%s.csv"%(year,quarter,name), index=False,encoding='utf-8_sig')

#start_F_score_choose(2022,2,function = 'q')
def stock_matrix(start_date,end_date,use = 'code',field='close'):
    i = 0
    code_list = datatbase_stock_code_list()
    for code in code_list:
        try:

            df = get_date_data(code,start_date,end_date)
            df[['close', 'open', 'high', 'low', 'volume','pctChg']] = df[
                ['close', 'open', 'high', 'low', 'volume','pctChg']].astype('float')

            df = df.rename(columns={field: df.loc[0,'code']})
            df = df[['date',df.loc[0,'code']]]
            if (i==0):
                 result = df
            else:
                 result = pd.merge(result,df,how = 'outer',on = 'date')
            i= i+1

        except Exception as e:
            print(e)
    result = result.drop(['date'],axis = 1)
    result_corr = result.corr()
    # plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置输出中文
    # plt.rcParams['axes.unicode_minus'] = False  # 避免负数无法输出
    # plt.rcParams['figure.figsize'] = (654, 654)
    # #plt.figure(dpi=1000)
    # rc = {'font.sans-serif': 'SimHei',
    #       'axes.unicode_minus': False}
    # sns.set(font_scale=0.3, rc=rc)  # 设置字体大小
    # sns.heatmap(result_corr,
    #         annot=True,  # 显示相关系数的数据
    #         center=0.5,  # 居中
    #         fmt='.2f',  # 只显示两位小数
    #         linewidth=0.5,  # 设置每个单元格的距离
    #         linecolor='blue',  # 设置间距线的颜色
    #         vmin=0, vmax=1,  # 设置数值最小值和最大值
    #         xticklabels=True, yticklabels=True,  # 显示x轴和y轴
    #         square=True,  # 每个方格都是正方形
    #         cbar=True,  # 绘制颜色条
    #         cmap='rainbow',  # 设置热力图颜色
    #         )
    # plt.savefig('D:/python_test/233.svg')
    # plt.show()
    #热力图对于大型热力图显示的不是很清楚

    #这样可以直接定位满足条件的值的横纵坐标
    pair_list = result_corr.where(result_corr>0.99999999).stack().index
    pair_list = list(pair_list) #需要转换类型，因为直接输出属于index_list类型
    #边遍历边删除会发生bug，因此有两种办法，办法A是先不删除，之后统一删除
    minus_list = []
    for pair in pair_list:
        if (pair[0]==pair[1]):
            minus_list.append(pair)
        else:
            pass
    #此为用差集删除
    pair_list = list(set(pair_list).difference(set(minus_list)))
    #方法B是用深拷贝进行遍历，在原本list上进行删除
    result_pair_list = []
    for pair in pair_list:
        pair = list(pair)
        if pair not in result_pair_list:
            if pair[::-1] not in result_pair_list:  #[::-1]为取反的意思
                result_pair_list.append(pair)

    print(result_pair_list)


    return
stock_matrix('2015-02-01','2022-09-01',field = 'pctChg')








