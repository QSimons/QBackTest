from main import *
class stock_backtest_storage():
    def __init__(self,code,start_date,end_date,fee=0.03):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.fee = fee
    def RSRS_backtest(self):
        df =get_date_data(self.code, self.start_date, self.end_date)
        df = technical_indicators(df).RSRS().get_result()
        df = df.dropna()
        buy_point = df[df.RSRS > 1]['date'].tolist()
        sell_point = df[df.RSRS < 0.8]['date'].tolist()
        stock_backtest(self.code,self.start_date,self.end_date,buy_point,sell_point).handle_backtest_starttime().handle_trade_day_index().handle_backtest().output_backtest()
        #注意如果要调用链式类则需要将全部函数都写入
        return

    def Double_average_backtest(self):  # 如果出现报错说list index out of range则说明日期不在数据库当中s
        df = get_date_data(self.code, self.start_date, self.end_date)
        df = technical_indicators(df).MA5().MA20().get_result()
        gold = df['MA5'] < df['MA20']  # 这里得到的是两个series
        dead = df['MA5'] >= df['MA20']
        g_corss_index = df[gold & dead.shift(1)]['date'].tolist()  # 这个其实是series进行比较
        d_cross_index = df[~(gold | dead.shift(1))]['date'].tolist()
        print(g_corss_index,d_cross_index)
        stock_backtest(self.code,self.start_date,self.end_date,g_corss_index,d_cross_index).handle_backtest_starttime().handle_trade_day_index().handle_backtest().output_backtest()
        return


# #'sh.300289','sh.600863','sh.601388','sh.600220','sz.002239','sh.600777','sh.601975','sz.002218'
# stock_list = ['sz.300289','sh.600863','sh.601388','sh.600220','sz.002239','sh.600777','sh.601975','sz.002218']
# for i in stock_list:
stock_backtest_storage('sh.600519','2015-02-01','2022-08-25').Double_average_backtest()

class etf_backtest():
    def __init__(self,code,start_date,end_date):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
    # target_index_code_list = ['sh000300','sh000905','sh000688','sz399293']
    # etf_code_list = ['561300', '510580', '588060', '159814']
    # etf_name_list = ['300增强', '中证500', '科创50', '创业大盘']
    # stock_zh_index_daily_em_df = ak.stock_zh_index_daily_em(symbol="sh000688")
