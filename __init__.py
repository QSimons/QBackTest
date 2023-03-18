from pytdx.hq import TdxHq_API

import MarketMonitor
api = TdxHq_API(auto_retry=True)

with api.connect('119.147.212.81', 7709):
    MarketMonitor.real_time_cal('sz.002528')