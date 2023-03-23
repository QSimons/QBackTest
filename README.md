# QBackTest 1.0.0
## 1.介绍 
* QBackTest是QSimons独立编写的python金融数据分析练习项目
* 实现策略买卖信号的发生，信号的处理和策略的回测。
在策略回测过程中可以输出回测结果图像和csv表格
* 在线数据源来源于开源金融数据库Akshare，数据输入方式可在utilis进行修改，支持本地数据导入
* 支持模块化引入计算指标，提升运算效率
* 本项目仅用于python金融分析学习交流使用，请勿用于投资等商业用途。



## 2.使用方法：
1.安装：请clone到本地使用，未来更新后会支持pip  


2.以下为一个双均线策略的样例：
```ruby  
import QBackTest.qbacktest as q
#导入包
code = '600007'
#定义回测目标股票代码
start_date = '20220101'
#定义回测开始时间
end_date = '20230101'
#定义回测结束时间
df = q.LoadDailyData(code,start_date,end_date).comb_MA5().comb_MA20().df
#模块化引入指标，指标项见utilis
b_index_list = df['MA5'] < df['MA20']   
s_index_list = df['MA5'] >= df['MA20']
g_corss_index = df[b_index_list & s_index_list.shift(1)]['日期'].tolist()  
d_cross_index = df[~(b_index_list | s_index_list.shift(1))]['日期'].tolist()
#策略实现，发出初始的交易信号
q.BackTest(code,start_date,end_date, g_corss_index,d_cross_index)
#策略回测
```  
3.回测结果可视化示例：
![回测结果可视化示例](https://github.com/QBackTest/image/双均线-示例回测.png)
## 3.维护
@QSimons
## 4.更新记录
1.0.0---上传所有本地代码，完成回测core部分的测试
## 5.未来更新
1.未来会添加更多的支持指标  
2.改善回测效率
