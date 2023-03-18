import main

import matplotlib.pyplot as plt
import pandas as pd
import pymysql


#38.3 29.96 18.38 8.8 3.32 1.24

def factor_sector_consistent(start_date,end_date):
    #警告模块
    db0 = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='stock_sectors'
    )
    db1 = pymysql.connect(
        host='localhost',
        user='root',
        password='root',
        database='stock_sectors_day'
    )
    cursor0 = db0.cursor()
    cursor1 = db1.cursor()
    sql0 = ' select `日期` from `银行d` order by `日期` desc limit 1;'  # 取得‘银行d'最后一行输入的数据的日期的tuple值
    cursor0.execute(sql0)
    data_end_date = cursor0.fetchall()[0][0]  #获取最新数据的最后日期
    print('警告，截至日期不得超过'+data_end_date)
    #日期限制模块
    start_date = main.trade_date(start_date, 0)
    end_date = main.trade_date(end_date, 0)
    date_list = main.get_trade_day_list()
    start_date_index = date_list.index(start_date)
    end_date_index = date_list.index(end_date)

    date_list = date_list[start_date_index:end_date_index+1]
    print(date_list)

    list_sectors_name_rise_f6 = []
    list_sectors_name_rise_f6_2dconsistent_num = [0]
    list_sectors_pctChg_next_day_point = [0]
    for date in date_list:
        sectors_name_rise_f6 = []
        list_sectors_pctChg_next_day = []
        sql1 = 'SELECT * from stock_sectors_day WHERE date =  %s limit 0,6;'%repr(date) #这个0,5不包括后面的5
        cursor1.execute(sql1)
        sectors_data_f6 = cursor1.fetchall()
        for i in range(0,6):
            sectors_name_rise_f6.append(sectors_data_f6[i][2])
            sql2 = 'SELECT `涨跌幅` from %s WHERE `日期`= %s;' % (sectors_data_f6[i][2],repr(main.trade_date(date, 1)))  # 注意在第一个%s不能加引号否则会报错
            cursor0.execute(sql2)
            sectors_pctChg_nextday = cursor0.fetchall()
            list_sectors_pctChg_next_day.append(sectors_pctChg_nextday[0][0])
            # 38.3 29.96 18.38 8.8 3.32 1.24
        print(list_sectors_pctChg_next_day)
        list_sectors_name_rise_f6.append(sectors_name_rise_f6)
        sectors_pctChg_next_day_point = list_sectors_pctChg_next_day[0]*0.383 + list_sectors_pctChg_next_day[1]*0.2996 + list_sectors_pctChg_next_day[2]*0.1838 + list_sectors_pctChg_next_day[3]*0.088 + list_sectors_pctChg_next_day[4]*0.032 + list_sectors_pctChg_next_day[5]*0.0124
        list_sectors_pctChg_next_day_point.append(sectors_pctChg_next_day_point)


    for i in range(1,len(list_sectors_name_rise_f6)):
        list_sectors_name_rise_f6_2dconsistent = set(list_sectors_name_rise_f6[i]) & set(list_sectors_name_rise_f6[i-1]) #list_sectors_name_rise_f6_2dconsistent指相邻相同的元素组成的list
        list_sectors_name_rise_f6_2dconsistent_num.append(len(list_sectors_name_rise_f6_2dconsistent)) #list_sectors_name_rise_f6_2dconsistent_num指list_sectors_name_rise_f6_2dconsistent的元素个数组成的list，开头为0






    df_lundong_data = main.get_date_data('sh.000001', start_date, end_date)
    i = 0
    for consistent_point in list_sectors_name_rise_f6_2dconsistent_num:
        df_lundong_data.loc[i,'consistent_point']=consistent_point
        i = i + 1
    j = 0
    for pctChg_point in list_sectors_pctChg_next_day_point:
        df_lundong_data.loc[j,'pctChg_point']=pctChg_point
        j = j + 1
    df_lundong_data[['open','close','high','low','pctChg','volume','amount','turn']] = df_lundong_data[['open','close','high','low','pctChg','volume','amount','turn']].astype('float')
    df_lundong_data.drop(df_lundong_data.tail(1).index,inplace=True)
    df_lundong_data.drop(df_lundong_data.head(1).index,inplace=True)

    print(df_lundong_data)

    #绘图模块+统计模块
    pearson_corr=df_lundong_data['pctChg'].corr(df_lundong_data['consistent_point'])
    kendall_corr=df_lundong_data['pctChg'].corr(df_lundong_data['consistent_point'],method='kendall')
    print('pearson相关系数%s,kendall相关系数%s'%(pearson_corr,kendall_corr))
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置输出中文
    plt.rcParams['axes.unicode_minus'] = False #避免负数无法输出
    plt.rcParams['figure.figsize'] = (19.2, 10.8)
    plt.figure(dpi=1000)
    fig,ax = plt.subplots(2,1) #创建空白画布
    ax[0].bar(df_lundong_data['date'],df_lundong_data['pctChg'])
    ax[0].set_title('日期-涨跌幅')  #这里其实本来应该考虑未来函数是涨跌幅，但也可以忽略
    ax[1].bar(df_lundong_data['date'],df_lundong_data['consistent_point'])
    ax[1].set_title('日期-连续指数')

    plt.savefig('D:/python_test/consistent_point.svg')
    plt.show()
    return
#factor_sector_consistent('2015-01-05','2022-07-25')

def factor_end_month(code,start_date,end_date): #使用整数月份进行回测
    month_x = []
    close_average_y = []
    end_5_close_average_y = []
    i = 0
    j = 0
    start_date = main.handle_backtest_starttime(code, start_date)
    stock_data = main.get_date_data(code, start_date, end_date)
    stock_data['date'] = pd.to_datetime(stock_data['date'], format='%Y-%m-%d')
    #print(stock_data.date)   #这个的数据类型为ｓｅｒｉｅｓ
    month_group = stock_data.groupby(stock_data['date'].apply(lambda x : (x.month)*(x.year)))
    for key,value in month_group: #分类结果不能直接输出，只能这样遍历输出
      if len(value)<15:  #去掉极端情况，保证交易天数达标
          pass
      else:
          i = i+1
          value = value.reset_index(drop=True)  # 重新索引
          value[['close', 'open', 'pctChg']] = value[['close', 'open', 'pctChg']].astype('float')
          value.drop(value.tail(5).index, inplace=True)
          month_close_average = value['pctChg'].sum()/len(value)
          month_x.append(str(value.iat[0,0].year) + '-' + str(value.iat[0,0].month))
          close_average_y.append(month_close_average)
          end_5_close_average_y.append((value.tail(5)['pctChg'].sum())/5)
          if value['pctChg'].sum()/len(value)>value.tail(5)['pctChg'].sum()/5:
             j = j + 1
    print('总周期有%s月，共%s月均价大于尾价，占比为%s'%(i,j,j/i))
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置输出中文
    plt.rcParams['axes.unicode_minus'] = False #避免负数无法输出

    plt.rcParams['figure.figsize'] = (19.2, 10.8)
    plt.figure(dpi=1000)
    fig, ax = plt.subplots()  # 创建空白画布
    stock_name = main.get_stock_basic_data(code).iat[0, 1]
    ax.plot(month_x,close_average_y,label='月度均价')
    ax.plot(month_x,end_5_close_average_y,label='月末均价')
    ax.set_xlabel('日期')
    ax.set_ylabel('价格')
    ax.set_title('月末价格相对月均价格研究')
    ax.legend()
    plt.savefig('D:/python_test/month_end_%s_%s-%s.svg'%(stock_name,start_date,end_date))
    plt.show()
    return
factor_end_month('sh.000001','2015-02-01','2022-07-01')
