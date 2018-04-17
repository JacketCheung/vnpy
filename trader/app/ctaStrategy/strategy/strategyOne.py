# encoding: UTF-8

"""
感谢Darwin Quant贡献的策略思路。
知乎专栏原文：https://zhuanlan.zhihu.com/p/24448511

策略逻辑：
1. 布林通道（信号）
2. CCI指标（过滤）
3. ATR指标（止损）

适合品种：螺纹钢
适合周期：15分钟

这里的策略是作者根据原文结合vn.py实现，对策略实现上做了一些修改，仅供参考。

"""

from __future__ import division


from vnpy.trader.vtObject import VtBarData
from vnpy.trader.vtConstant import EMPTY_STRING
from vnpy.trader.app.ctaStrategy.ctaTemplate import (CtaTemplate, 
                                                     BarGenerator,
                                                     )
from vnpy.trader.app.ctaStrategy.ctaTempleteExtension import zhibiao
from datetime import datetime,time

from vnpy.trader.language.chinese.constant import *
from strategyZero import ZeroStrategy
########################################################################
class OneStrategy(ZeroStrategy):
    def __init__(self,ctaEngine,setting):
        super(OneStrategy, self).__init__(ctaEngine, setting)
        # YUNX
        self.yunCount = 0
        self.yunLastTick = None
    def onTick(self, tick):

            """收到行情TICK推送（必须由用户继承实现）"""
            self.bg.updateTick(tick)
            self.am.updateTick(tick)
            am = self.am

            if not self.stopcount:
                fangxiang = None
                price = None
                if tick.datetime.second > 53:
                    if am.diff > 0 and am.macd < 0 and am.lastmacd > 0:
                        fangxiang = duo
                        price = tick.bidPrice1

                    elif am.macd > 0 and am.lastmacd < 0:
                        if self.pos > 0:

                            fangxiang = duoping
                            price = tick.askPrice1
                        elif self.longOrder is not None:
                            self.cancelVtOrder(self.longOrder, u'平多仓时候', 'long')

                    if am.diff < 0 and am.macd > 0 and am.lastmacd < 0:

                        fangxiang = kong
                        price = tick.askPrice1

                    elif am.macd < 0 and am.lastmacd > 0:
                        if self.pos < 0:
                            fangxiang = kongping
                            price = tick.bidPrice1
                        elif self.shortOrder is not None:
                            self.cancelVtOrder(self.shortOrder, u'平空仓时候', 'short')
                self.chulikaipingcang(fangxiang, price)
                if fangxiang in [duo,kong,duoping,kongping]:
                            if self.yunCount == 0:
                                self.yunCount = 5
                if self.yunCount > 0:
                                self.yunCount -= 1
                                self.yunchulifangxiang(fangxiang,tick)
    def yunchulifangxiang(self,fangxiang,tick):
        if self.yunLastTick is not None:
            if self.yunLastTick.datetime.minute != tick.datetime.minute:
                if self.yunCount < 3:
                    fang,price = self.tickCelve(tick)
                    self.chulikaipingcang(fang,price)
            else:
                if self.yunCount == 0:
                    fang,price == self.tickCelve(tick)
                    self.chulikaipingcang(fang,price)

duo = 100
duoping = 50
paiduiduo = 150
paiduiduoping = 155
kong = 200
kongping = 250
paiduikong = 400
paiduikongping = 500
kaipantime = time(hour=9, minute=0)
zaoxiutime = time(hour=10, minute=15)
zaoxiuendtime = time(hour=10, minute=30)
shoupantime = time(hour=15, minute=0)
wuxiutime = time(hour=11, minute=30)
zhongwukaipantime = time(hour=13, minute=30)