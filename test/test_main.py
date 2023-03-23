
import qbacktest as q

'''
测试样例：双均线策略：
'''
code = '600007'
#定义回测目标股票代码
start_date = '20220101'
#定义回测开始时间
end_date = '20230101'
#定义回测结束时间
df = q.LoadDailyData(code,start_date,end_date).comb_MA5().comb_MA20().df
#模块化引入指标，指标项见utilis
b_index_list = df['MA5'] > df['MA20']
s_index_list = df['MA5'] <= df['MA20']
g_corss_index = df[b_index_list & s_index_list.shift(1)]['日期'].tolist()
d_cross_index = df[~(b_index_list | s_index_list.shift(1))]['日期'].tolist()
#策略实现，发出初始的交易信号
q.BackTest(code,start_date,end_date, g_corss_index,d_cross_index)
#策略回测