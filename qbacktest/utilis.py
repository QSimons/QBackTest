
import akshare as ak
import pandas as pd
class LoadDailyData:
    '''
    工具类：加载
    comb自由组合进行所需的数据加载
    '''
    def __init__(self,code,start_date,end_date):
        self.code = code
        self.start_date = start_date
        self.end_date = end_date
        self.df = ak.stock_zh_a_hist(symbol=self.code, period="daily", start_date=self.start_date,end_date=self.end_date,adjust="hfq")
    def comb_MA5(self):
        self.df['MA5'] = self.df['收盘'].rolling(window=5).mean()
        return self

    def comb_MA10(self):
        self.df['MA10'] = self.df['收盘'].rolling(window=10).mean()
        return self

    def comb_MA20(self):
        self.df['MA20'] = self.df['收盘'].rolling(window=20).mean()
        return self
    def comb_KDJ(self,n = 9,K0 = 50,D0 = 50):
        temp_data = self.df
        temp_data['Ln'] = temp_data['low'].rolling(window = n).min()
        temp_data['Hn'] = temp_data['high'].rolling(window = n).max()
        i = 0 #用于标记，第一次要将KDJ值标记为初始量
        for index in temp_data.index.tolist():
            print(pd.isnull(temp_data.loc[index,'Ln']))
            if (pd.isnull(temp_data.loc[index,'Ln']) or pd.isnull(temp_data.loc[index,'Hn'])): #判断是否为空，为空则不进行计算
                pass
            else:
                print(index)
                self.df.loc[index,'RSV'] = (temp_data.loc[index,'close']-temp_data.loc[index,'Ln'])/(temp_data.loc[index,'Hn']-temp_data.loc[index,'Ln'])
                if (i==0):
                    self.df.loc[index,'K'] = K0
                    self.df.loc[index,'D'] = D0
                    self.df.loc[index,'J'] = 3*K0 - 2*D0
                    i = i +1
                else:
                    self.df.loc[index,'K'] = (2 * self.df.loc[index-1,'K'])/3 + (self.df.loc[index,'RSV'])/3
                    self.df.loc[index, 'D'] = (2 * self.df.loc[index-1,'D'])/3 + (self.df.loc[index,'K'])/3
                    self.df.loc[index, 'J'] = 3*self.df.loc[index,'K'] - 2*self.df.loc[index, 'D']
        return self

