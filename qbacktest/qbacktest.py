import core

class BackTest():
    def __init__(self,code,start_date,end_date,b_date_list,s_date_list,fee=0.03):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.b_date_list = b_date_list
        self.s_date_list = s_date_list
        self.fee = fee
        obj = core.QCore(self.code,self.start_date,self.end_date,self.b_date_list,self.s_date_list).handle_trade_day_index().handle_backtest().output_backtest()

    '''
    例子：双均线
    '''
    # def Double_average_backtest(self):  # 如果出现报错说list index out of range则说明日期不在数据库当中s
    #     df = utilis.LoadDailyData(self.code,self.start_date,self.end_date).comb_MA5().comb_MA20().df
    #     gold = df['MA5'] < df['MA20']  # 这里得到的是两个series
    #     death = df['MA5'] >= df['MA20']
    #     g_corss_index = df[gold & death.shift(1)]['日期'].tolist()  # 这个其实是series进行比较
    #     d_cross_index = df[~(gold | death.shift(1))]['日期'].tolist()
    #     print(g_corss_index,d_cross_index)
    #
    #     core.QCore(self.code,self.start_date,self.end_date,g_corss_index,d_cross_index).handle_trade_day_index().handle_backtest().output_backtest()
    #     return