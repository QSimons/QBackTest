import akshare
import pandas
import requests

sh_df = akshare.stock_sh_a_spot_em()
sz_df = akshare.stock_sz_a_spot_em()
data_df = pandas.concat([sh_df, sz_df])
stock_list = data_df['代码'].tolist()
huanshou_xishu = 10
res_dict = {}
for i in stock_list:
    df = akshare.stock_zh_a_hist(symbol=i, period="daily", start_date="20230306",
                                                end_date='20230310', adjust="")
    if(len(df)==5):
        if(df['收盘'].tolist()[-1]<=8):
            deal_am_list = df['成交量'].tolist()
            ave_4_huanshou = sum(deal_am_list[0:4])/4
            if(ave_4_huanshou*huanshou_xishu < deal_am_list[-1]):
                res_dict[i] = deal_am_list[-1]
                print(df)


a = sorted(res_dict.items(), key=lambda x: x[1])
print(a)