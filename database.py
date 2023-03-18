import datetime

import main
import sqlalchemy
import pymysql
import pandas as pd
import baostock as bs
import akshare as ak


#数据库中包含stock_date和各个股票的日期数据
def input_database_stocks(mode='b'): #默认前复权,默认为前复权而输入
 list0 = main.stock_code('2022-09-01')
 print(list0)
 for index,code in list0.code.items():
     lg = bs.login()
     rs = bs.query_history_k_data_plus(code,
                                       "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg",
                                       start_date='2015-01-01', end_date='2022-09-01',
                                       frequency="d", adjustflag="2")
     data_list = []
     while (rs.error_code == '0') & rs.next():
         data_list.append(rs.get_row_data())
     result = pd.DataFrame(data_list, columns=rs.fields)
     print(result)
     conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stocks_b',encoding='utf8')
     pd.io.sql.to_sql(result,code+'d',conn,if_exists = 'replace')
 return


def input_stock_basic_data():
    list0 = main.stock_code('2022-09-22')
    print(list0)
    for index, code in list0.code.items():
        result = main.get_stock_basic_data(code)
        conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stock_basic_data', encoding='utf8')
        pd.io.sql.to_sql(result,code, conn, if_exists='replace')
        print(result)
    return
#input_stock_basic_data()


def input_database_stock_sectors(): #单次使用过的函数 #2022.7.14更新
    stock_board_industry_name_em_df = ak.stock_board_industry_name_em()
    stock_board_list = stock_board_industry_name_em_df['板块名称'].tolist()
    for stock_board_name in stock_board_list:
        stock_board_industry_hist_em_df = ak.stock_board_industry_hist_em(symbol=stock_board_name,
                                                                          start_date="20150101",
                                                                          end_date="20220729", adjust="")
        print(stock_board_industry_hist_em_df)

        conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stock_sectors',encoding='utf8')
        pd.io.sql.to_sql(stock_board_industry_hist_em_df,stock_board_name+'d',conn,if_exists = 'replace')
    return
#input_database_stock_sectors()

def input_etf_data():
    etf_code_list = ['561300','510580','159781','159814']
    etf_name_list = ['300增强','中证500','双创50','创业大盘']
    i = 0
    for code in etf_code_list:
        etf_date_data = ak.fund_etf_fund_info_em(fund=code, start_date="20150101", end_date="20220825")
        etf_date_data = etf_date_data.sort_values(by='净值日期', ascending=True)
        etf_date_data = etf_date_data.reset_index(drop=True)
        print(etf_date_data)
        conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/etf', encoding='utf8')
        pd.io.sql.to_sql(etf_date_data, code, conn, if_exists='replace')
    return





def stock_sectors_input(): #直接将所有的板块表联合到一起
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='stock_sectors'
    )
    cursor = db.cursor()
    sql0 = 'SHOW TABLES FROM stock_sectors'
    cursor.execute(sql0)
    stock_sectors_list = cursor.fetchall()
    stock_sectors_list = list(stock_sectors_list)
    for i in range(0, len(stock_sectors_list)):
        stock_sectors_list[i] = ''.join(stock_sectors_list[i])
    #str_stock_sectors = ','.join(stock_sectors_list) 直接传入所有的会超出sql的同时传入限制
    # stock_sectors_list1 = stock_sectors_list[:61]
    # stock_sectors_list2 = stock_sectors_list[61:]
    # str_stock_sectors1  = ','.join(stock_sectors_list1)
    # str_stock_sectors2  = ','.join(stock_sectors_list2)
    # all_str_stock_sectors = [str_stock_sectors1,str_stock_sectors2]

    trade_date_list = main.get_trade_day_list();

    df_stock_sectors_per_day = pd.DataFrame(columns=['date','name','open','close','high','low','pctChg','AmtChg','volume','amount','amplitude','turn'])
    temp_df_stock_sectors_per_day = pd.DataFrame(columns=['date', 'name', 'open', 'close', 'high', 'low', 'pctChg', 'AmtChg', 'volume', 'amount', 'amplitude', 'turn'])
    for date in trade_date_list:  #AmtChg为涨跌额，amplitude是振幅
        i = 0
        temp_df_stock_sectors_per_day = temp_df_stock_sectors_per_day.drop(index=temp_df_stock_sectors_per_day.index)
        for str_stock_sector in stock_sectors_list:
          sql1 = 'SELECT * from %s WHERE `日期` =  %s;'%(str_stock_sector,repr(date)) #where语句的等号后面的字符必须使用''
          cursor.execute(sql1)
          data = cursor.fetchall()
          if len(data)== 0: #使用长度来判断列表是否为空
             pass
          else:
           day_data = list(data[0])
           day_data[0] = day_data[1]
           day_data[1] = str_stock_sector
           temp_df_stock_sectors_per_day.loc[i] = day_data
           i = i+1
        temp_df_stock_sectors_per_day= temp_df_stock_sectors_per_day.sort_values(by='pctChg',ascending = False)#这里可以更改数据的排序方式！！！！
        frames = [df_stock_sectors_per_day, temp_df_stock_sectors_per_day]
        df_stock_sectors_per_day = pd.concat(frames)
        df_stock_sectors_per_day = df_stock_sectors_per_day.reset_index(drop=True)
        print(df_stock_sectors_per_day)
    conn = sqlalchemy.create_engine('mysql+pymysql://root:root@localhost:3306/stock_sectors_day', encoding='utf8')
    pd.io.sql.to_sql(df_stock_sectors_per_day,'stock_sectors_day', conn, if_exists='replace')
    return
#stock_sectors_input()




def compare_table(): #目的是为了比较mysql中的table和实际股票的区别来更新，去掉退市股票并且增加新上市股票
 today = datetime.date.today()
 db = pymysql.connect(
  host = 'localhost',
  user = 'root',
  password = 'root',
  database = 'stocks'
 )
 cursor = db.cursor()
 sql = 'SHOW TABLES FROM STOCKS'
 cursor.execute(sql)
 result = cursor.fetchall()
 result = list(result)
 for i in range(0,len(result)):
    result[i] = ''.join(result[i])
 now_stock = main.stock_code(main.trade_date(str(today), -1)) #导入包时要import datetime 否则会报错:attribute error
 now_stock_list = now_stock['code'].tolist() #.tolist()可以将只有一列的dataframe转化为list
 for i in range(0,len(now_stock)):
  now_stock_list[i] = now_stock_list[i] + 'd'
 now_stock_list.append('stock_date')

 disappear_list = set(result).difference(set(now_stock_list)) #目前数据库中含有的退市个股
 new_list = set(now_stock_list).difference(set(result)) #目前数据库没有的新上市个股
 print(result)
 list0 = [disappear_list, new_list, result]
 return list0







def update_stocks_d(mode = 'b'):
    if (mode == 'b'): #前复权
        database = 'stocks_b'
        adjust_flag = '2'
        database_path = 'mysql+pymysql://root:root@localhost:3306/stocks_b'
    elif (mode == 'n'): #不复权
        database = 'stocks'
        adjust_flag = '3'
        database_path = 'mysql+pymysql://root:root@localhost:3306/stocks'
    else:
        print('所选模式错误')

    today = datetime.date.today() #注意today的数据类型为datatime.date不是str，需要转换
    data_day_end = main.trade_date(str(today), -1) #保证昨天的数据能被加载
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database= database
    )
    cursor = db.cursor()
    for del_code in compare_table()[0]: #删除退市股票
     d_code = '`'+del_code+'`'
     sql0 = 'DROP TABLE IF EXISTS %s' %d_code
     cursor.execute(sql0)

    list_now = compare_table()[2]# 目前数据库中含有的股票，如果其中混入了新股会报错,还要删掉其中的stock_date
    list_now.remove('stock_date') #这个不能和上一串代码合并，否则会报错，因为这个不能写为等式的形式
    for code in list_now :
        code0 = code[:-1]
        code1 = '`'+code+'`'
        sql1 = ' select `date` from %s order by `date` desc limit 1;'%code1 #取得最后一行输入的数据的日期的tuple值
        cursor.execute(sql1)
        #result = ''.join(list((cursor.fetchall()))[0]) #获得最后一行日期的str值
        result = cursor.fetchall()[0][0]
        data_day_start = main.trade_date(result, 1)
        sql2 = ' select `index` from %s order by `date` desc limit 1;' % code1  # 取得最后一行输入的数据的日期的index值,注意index需要带上``，这个是关键词
        cursor.execute(sql2)
        index_start =cursor.fetchall()[0][0]+1 #这个tuple中包含数字，不能转化成list再转化为字符串再转换为int


        lg = bs.login()
        rs = bs.query_history_k_data_plus(code0,
                                          "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg",
                                          start_date= data_day_start, end_date=data_day_end,
                                          frequency="d", adjustflag= adjust_flag)
        data_list = []
        while (rs.error_code == '0') & rs.next():
             data_list.append(rs.get_row_data())
        result1 = pd.DataFrame(data_list, columns=rs.fields)
        list1 = range(index_start,index_start+len(result1))
        result1.index = list1
        print(result1,index_start)



        if result1.empty == True:
          print(code+'已经停止更新数据，所更新数据为空')
        else:
          conn = sqlalchemy.create_engine(database_path, encoding='utf8')
          pd.io.sql.to_sql(result1, code0 + 'd', conn, if_exists='append')

    for code2 in compare_table()[1]:
        code2 = code2[:-1]
        lg = bs.login()
        rs = bs.query_history_k_data_plus(code2,
                                          "date,code,open,high,low,close,volume,amount,adjustflag,turn,pctChg",
                                          start_date='2015-01-01', end_date=data_day_end,
                                          frequency="d", adjustflag=adjust_flag)
        data_list = []
        while (rs.error_code == '0') & rs.next():
            data_list.append(rs.get_row_data())
        result2 = pd.DataFrame(data_list, columns=rs.fields)

        conn = sqlalchemy.create_engine(database_path, encoding='utf8')
        pd.io.sql.to_sql(result2, code2 + 'd', conn, if_exists='replace')


    return
#update_stocks_d(mode = 'n')