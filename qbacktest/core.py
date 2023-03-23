
import utilis
import matplotlib.pyplot as plt
class QCore:
    '''
    QBackTest核心，处理发出买卖信号为回测结果
    '''
    def __init__(self, code, start_date, end_date, b_date_list, s_date_list, fee=0.03):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.b_date_list = b_date_list
        self.s_date_list = s_date_list
        self.fee = fee
        self.df = utilis.LoadDailyData(code,start_date,end_date).df


    def buy_check(self,b_index): #检查买入信号发生后一天能否买入
        if (b_index[-1] == self.df.tail(1).index[0]):
            del b_index[-1]
        else:
            for i in b_index:
                today_close = self.df.loc[i, '收盘']
                tomorrow_open = self.df.loc[i + 1, '开盘']
                tomorrow_open_max = round(today_close*1.09,2)
                if (tomorrow_open >= tomorrow_open_max):
                    b_index.remove(i)
                    print('%s 在 %s 发生开盘涨停，无法买入' % (self.code,self.df.loc[i + 1, '日期']))
                if (self.df.loc[i + 1, '成交量']==0):
                    b_index.remove(i)
                    print('%s 在 %s 发生停牌，无法买入' % (self.code,self.df.loc[i + 1, '日期']))
        return b_index

    def sell_check(self,s_index):
        if (s_index[-1] == self.df.tail(1).index[0]):
            del s_index[-1]
        else:
            for i in s_index:
                today_close = self.df.loc[i, '收盘']
                tomorrow_close = self.df.loc[i + 1, '收盘']
                tomorrow_close_min = round(today_close * 0.91, 2)
                if (tomorrow_close_min >= tomorrow_close):
                    s_index.remove(i)
                    print('%s 在 %s 发生尾盘跌停，无法卖出' % (self.code, self.df.loc[i + 1, '日期']))
                if (self.df.loc[i + 1, '成交量']==0):
                    s_index.remove(i)
                    print('%s 在 %s 发生停牌，无法卖出' % (self.code,self.df.loc[i + 1, '日期']))
        return s_index

    def handle_trade_day_index(self):
        b_index_list = []
        s_index_list = []
        comb_b_s_list = []
        print('buy raw signal generate %s ' % (self.b_date_list))
        print('sell raw signal generate %s ' % (self.s_date_list))
        [b_index_list.append(self.df.loc[(self.df['日期'] == i)].index[0]) for i in self.b_date_list]
        [s_index_list.append(self.df.loc[(self.df['日期'] == i)].index[0]) for i in self.s_date_list]
        b_index_list = QCore.buy_check(self, b_index_list)
        s_index_list = QCore.sell_check(self,s_index_list)
        b_index_list = [(i,'b') for i in b_index_list]

        s_index_list = [(i,'s') for i in s_index_list]
        comb_b_s_rlist = b_index_list + s_index_list
        comb_b_s_rlist.sort(key=lambda x: x[0])
        comb_b_s_rlist = comb_b_s_rlist[comb_b_s_rlist.index((b_index_list[0][0],'b')):]
        side = 'b'
        for i in comb_b_s_rlist:
            if(i[1] == side):
                comb_b_s_list.append(i)
                if(side == 'b'):
                    side = 's'
                else:
                    side = 'b'
        self.b_index_list = [i[0] for i in comb_b_s_list if i[1]=='b']
        self.s_index_list = [i[0] for i in comb_b_s_list if i[1]=='s']
        return self
    def do_buy_day(self,index):
        self.property = self.property - self.df.loc[index, '开盘'] + self.df.loc[index, '收盘']
        self.cash = self.cash - self.df.loc[index, '开盘']
        self.df.loc[index, 'property'] = self.property
        self.df.loc[index, 'cash'] = self.cash
        self.property_list.append(self.property)
        self.cash_list.append(self.cash)
        print('已在 %s 进行了买入操作' % (self.df.loc[index, '日期']))
        return self
    def do_sell_day(self,index):
        self.property = self.property - self.df.loc[index - 1, '收盘'] + self.df.loc[index, '收盘'] - self.fee
        self.cash = self.cash + self.df.loc[index, '收盘'] - self.fee
        self.df.loc[index, 'property'] = self.property
        self.df.loc[index, 'cash'] = self.cash
        self.property_list.append(self.property)
        self.cash_list.append(self.cash)
        print('已在 %s 进行了卖出操作' % (self.df.loc[index, '日期']))
        return self
    def full_condition(self,index):
        self.property = self.property - self.df.loc[index - 1, '收盘'] + self.df.loc[index, '收盘']
        self.df.loc[index, 'property'] = self.property
        self.df.loc[index, 'cash'] = self.cash
        return self
    def empty_condition(self,index):
        self.df.loc[index, 'property'] = self.property
        self.df.loc[index, 'cash'] = self.cash
        return self

    def initial_backtest(self):
        #必须初始化数据类型
        # self.df[['开盘', 'close']] = self.df[['开盘', 'close']].astype('float')
        #裁剪df使得其从第一次买入开始,到最后一次卖出结束
        self.df = self.df[self.b_index_list[0]:self.s_index_list[-1] + 1]
        #初始化统计量
        self.property_list = []
        self.cash_list = []
        self.property = self.df.loc[self.b_index_list[0], '开盘']
        self.cash = self.df.loc[self.b_index_list[0], '开盘']

    def handle_backtest(self):
        QCore.initial_backtest(self)
        b_to_s_dict = dict(zip(self.b_index_list,self.s_index_list))
        full_list = []
        for b, s in b_to_s_dict.items():
             list_temp = list(range(b+1,s)) #range和list类型不能相加，必须转换后才能相加
             full_list = full_list + list_temp
        for index in self.df.index.values:
            if index in self.b_index_list:
                QCore.do_buy_day(self,index)
            elif index in self.s_index_list:
                QCore.do_sell_day(self,index)
            elif index in full_list:
                QCore.full_condition(self,index)
            else:
                QCore.empty_condition(self,index)

        return self




    def output_backtest(self):
        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.figsize'] = (19.2, 10.8)
        plt.figure(dpi=1000)
        self.df.plot(x='日期', y=['收盘', 'property'])
        stock_name = self.code
        plt.title(stock_name + '回测模型', fontsize=15)
        plt.xlabel("时间", fontsize=13)
        plt.ylabel("权益", fontsize=13)
        plt.savefig('D:/python_test/backtest/backtest-%s-%s.svg' % (stock_name, self.start_date))
        plt.legend()
        plt.show()
        self.df.to_csv('D:/python_test/backtest/backtest-%s-%s.csv' % (stock_name, self.start_date), index=True, encoding='utf-8_sig')
