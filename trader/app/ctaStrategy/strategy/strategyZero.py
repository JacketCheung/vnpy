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
########################################################################
class ZeroStrategy(CtaTemplate):
    """基于布林通道的交易策略"""
    className = 'ZeroStrategy'
    author = u'用Python的交易员'


    initDays = 10                       # 初始化数据所用的天数
    fixedSize = 1                       # 每次交易的数量


    # 参数列表，保存了参数的名称
    paramList = ['name',
                 'className',
                 'author',
                 'vtSymbol',
                 'initDays',
                 'fixedSize']    

    # 变量列表，保存了变量的名称
    varList = ['inited',
               'trading',
               'pos'
               ]
    
    # 同步列表，保存了需要保存到数据库的变量名称
    syncList = ['pos']

    #----------------------------------------------------------------------
    def __init__(self, ctaEngine, setting):
        """Constructor"""
        super(ZeroStrategy, self).__init__(ctaEngine, setting)
        
        self.bg = BarGenerator(self.onBar)        # 创建K线合成器对象
        self.am = zhibiao()

        #仓位
        self.shortOrder = None
        self.longOrder = None
        #最小价差变动
        self.tickadd = 1

        #有无夜盘和 相关的时间
        self.yepan = True
        self.yepanhour = 23
        self.yepanminute = 00
        self.stopcount = 0
        #断网变量相关
        self.lastbardatetime = None
        self.didinited = False

        
    #----------------------------------------------------------------------
    def on30minBar(self, bar):
        """"""
        
        
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略初始化' %self.name)
        
        # 载入历史数据，并采用回放计算的方式初始化策略数值
        initData = self.loadBar(self.initDays)
        for bar in initData:
            self.onBar(bar)
        self.didinited = True
        self.putEvent()

    #----------------------------------------------------------------------
    def onStart(self):
        """启动策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略启动' %self.name)
        self.putEvent()

    #----------------------------------------------------------------------
    def onStop(self):
        """停止策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略停止' %self.name)
        self.putEvent()
    def cancelVtOrder(self,order,yuanyin,fangxiang):
        print(yuanyin,'cancle')
        self.cancelOrder(order)
        if fangxiang == 'long':
            self.longOrder = None
        elif fangxiang == 'short':
            self.shortOrder = None
    #----------------------------------------------------------------------
    def onTick(self, tick):

        """收到行情TICK推送（必须由用户继承实现）"""
        self.bg.updateTick(tick)
        self.am.updateTick(tick)
        am = self.am

        if not self.stopcount:
            fangxiang = None
            price = None
            if tick.datetime.second > 53 :
                if am.diff > 0 and am.macd < 0 and am.lastmacd > 0 :
                    fangxiang = duo
                    price = tick.bidPrice1

                elif am.macd > 0 and am.lastmacd < 0:
                    if self.pos>0:

                       fangxiang = duoping
                       price = tick.askPrice1
                    elif self.longOrder is not None:
                        self.cancelVtOrder(self.longOrder,u'平多仓时候','long')

                if am.diff < 0 and am.macd > 0 and am.lastmacd < 0:

                    fangxiang = kong
                    price = tick.askPrice1

                elif am.macd < 0 and am.lastmacd > 0:
                    if self.pos < 0:
                      fangxiang = kongping
                      price = tick.bidPrice1
                    elif self.shortOrder is not None:
                        self.cancelVtOrder(self.shortOrder,u'平空仓时候','short')


            self.chulikaipingcang(fangxiang,price)
    def checkPingcang(self,bar):
        am = self.am
        fangxiang = None
        price = None
        if self.pos > 0 and self.longOrder is not None and am.lastmacd > 0 and am.mj < 0:
            self.cancelVtOrder(self.longOrder, u'必须平多','long')
            fangxiang = duoping
            price = am.tick.bidPrice1
        elif self.pos < 0 and self.shortOrder is not None and am.lastmacd < 0 and am.mj > 0:
            self.cancelVtOrder(self.shortOrder, u'必须平空','short')
            self.chulikaipingcang(kongping, am.tick.bidPrice1)
            fangxiang = kongping
            price = am.tick.askPrice1
        self.chulikaipingcang(fangxiang, price)
        #----------------------------------------------------------------------
    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""


         #检查是否有效的交易时间
        if self.notintradingTime(bar):
            return

        self.bg.updateBar(bar)
        self.am.updateBar(bar)
        am = self.am
        if self.didinited:
         print('zhibiao','macd',am.macd,'diff',am.diff,'mj',am.mj,'time',bar.datetime,'end')
        #检查是否断网
        self.checkIfConnecting(bar)

        self.lastbardatetime = bar.datetime
        self.checkPingcang(bar)

        self.am.endBar()
        self.putEvent()

    #----------------------------------------------------------------------

    #----------------------------------------------------------------------
    def onOrder(self, order):
        """收到委托变化推送（必须由用户继承实现）"""
        if order.status == STATUS_NOTTRADED:
            self.reactOrder(order,order.vtOrderID)
        elif order.status == STATUS_ALLTRADED or order.status == STATUS_CANCELLED:
            self.reactOrder(order,None)
        print 'order', order.price,order.direction,order.offset      ,order.status,order.vtOrderID,order.orderTime,self.pos,self.am.tick.datetime

        pass

    #----------------------------------------------------------------------
    def reactOrder(self,order,vtOrderID):
        print 'react',order.direction,order.offset
        if (order.direction == DIRECTION_LONG and order.offset == OFFSET_OPEN) \
                or \
                (order.direction == DIRECTION_SHORT and (order.offset == OFFSET_CLOSE or order.offset == OFFSET_CLOSETODAY or order.offset == OFFSET_CLOSEYESTERDAY)):
            print 'enterlong'
            self.longOrder = vtOrderID
        elif (order.direction == DIRECTION_LONG and (order.offset == OFFSET_CLOSE  or order.offset == OFFSET_CLOSETODAY or order.offset == OFFSET_CLOSEYESTERDAY)) \
                or \
                (order.direction == DIRECTION_SHORT and order.offset == OFFSET_OPEN):
            print 'entershort'
            self.shortOrder = vtOrderID
        else: print('enteranother')
    def onTrade(self, trade):
        # 发出状态更新事件
        self.reactOrder(trade,None)
        print 'trade',trade.price,trade.direction,trade.offset,trade.tradeTime

        self.putEvent()

    #----------------------------------------------------------------------
    def onStopOrder(self, so):
        """停止单推送"""
        pass
    

#----------------------------------------------------------------------
    '''仓位函数'''

    def chulikaipingcang(self, fangxiang, price):
        if self.didinited:
            if fangxiang == duo:
                if self.pos == 0 and self.longOrder is None:
                    self.longOrder = 0
                    print  'buybuy'
                    self.buy(price, 1)
                elif self.pos < 0 and self.shortOrder is None:
                    self.shortOrder = 0
                    self.cover(price , 1)
                    self.buy(price, 1)

            elif fangxiang == kong:
                if self.pos == 0  and self.shortOrder is None:
                    self.shortOrder = 0
                    self.short(price , 1)
                elif self.pos > 0 and self.longOrder is None:
                    self.longOrder = 0
                    self.sell(price , 1)
                    self.short(price , 1)

            elif fangxiang == duoping:
                if self.pos > 0 and self.longOrder is None:
                    self.longOrder = 0
                    self.sell(price,1)


            elif fangxiang == kongping:
                if self.pos < 0 and self.shortOrder is None:
                    self.shortOrder = 0
                    self.cover(price,1)







        # ----------------------------------------------------------------------
    '''断网判断及处理函数'''
    '''目前的逻辑是根据两个bar的时间间隔来判断是否断网，一个可能的风险当市场上两笔交易的间隔长于两分钟时，会错认为也是断网了，这个在不活跃品种也较容易出现。不过一般出现这种情况较少。'''
    def closeAllPosistion(self, price):
        '''出意外如断网时平仓'''
        self.cancelAll()
        print('--closeallpos--')
        if self.pos > 0:
            self.short(price - self.tickadd, abs(self.pos))
        elif self.pos < 0:
            self.cover(price + self.tickadd, abs(self.pos))

        # ----------------------------------------------------------------------

    # ----------------------------------------------------------------------
    def iscontinueTime(self, firstdatetime, seconddatetime):
        '''判断是否为连续的时间'''
        if (firstdatetime.hour == seconddatetime.hour and firstdatetime.minute + 1 == seconddatetime.minute) \
                or (
                firstdatetime.hour == seconddatetime.hour - 1 and firstdatetime.minute == 59 and seconddatetime.minute == 0):
            return True

    # ----------------------------------------------------------------------
    def isTradeContinueTime(self, firstdatetime, seconddatetime):
        '''判断是否为连续的交易时间'''
        if self.iscontinueTime(firstdatetime, seconddatetime):
            return True
        elif firstdatetime.hour == 10 and (
                firstdatetime.minute == 15 or firstdatetime.minute == 14) and seconddatetime.hour == 10 and (seconddatetime.minute == 30 or seconddatetime.minute == 31):
            return True
        elif firstdatetime.hour == 11 and (
                firstdatetime.minute == 29 or firstdatetime.minute == 30) and seconddatetime.hour == 13 and (seconddatetime.minute == 30 or seconddatetime.minute == 31):
            return True
        elif self.yepan and (seconddatetime.hour == 9 or (seconddatetime.hour == 8 and seconddatetime.minute == 59)) and (
                    firstdatetime.hour == self.yepanhour or (
                    firstdatetime.hour == self.yepanhour - 1 and firstdatetime.minute == 59)):
                return True
        elif (firstdatetime.hour == 15 or (firstdatetime.hour == 14 and firstdatetime.minute ==59)) and ((seconddatetime.hour == 9 and seconddatetime.minute == 0) or (seconddatetime.hour == 8 and seconddatetime.minute == 59) ):
            return  True
        elif  ((firstdatetime.hour == 14 and firstdatetime.minute == 59) or firstdatetime.hour == 15 ) and (seconddatetime.hour == 21 or (seconddatetime.hour == 20 and seconddatetime.minute ==59)):
            return True
        elif ((firstdatetime.hour == 23 and firstdatetime.minute == 59) and (seconddatetime.hour == 0 and seconddatetime.minute ==0)) or ((firstdatetime.hour == 0 and firstdatetime.minute == 59) and(( seconddatetime.hour == 9 and seconddatetime.minute == 0) )):
            return  True

        else:
            print('dus conne',firstdatetime,seconddatetime)
            return False
    # ----------------------------------------------------------------------
    def handleDisConnected(self, price):
        print('DISCONNECTED', self.lastbardatetime, self.am.datetime)
        self.closeAllPosistion(price)
        self.stopcount = 15

    def notintradingTime(self, bar):
        if bar.datetime.hour == 15 and bar.datetime.minute > 0:
            return True
    def checkIfConnecting(self, bar):
        if self.lastbardatetime is None:
            self.lastbardatetime = bar.datetime
        else:
            if not self.isTradeContinueTime(self.lastbardatetime, bar.datetime):
                # 断网了，需要处理断网状态
                self.handleDisConnected(bar.close)
            # 没有断网
            else:
                if self.stopcount > 0:
                    self.stopcount -= 1

    def barkaicang(self, bar):
        am = self.am
        if not  self.stopcount:
            fangxiang = None
            price = bar.close
            if am.diff >0 and am.macd < 0 and am.lastmacd > 0 :
                fangxiang = duo
            elif am.macd > 0 and am.lastmacd < 0:
                fangxiang = duoping
            elif am.diff < 0 and am.macd > 0 and am.lastmacd <0:
                fangxiang = kong
            elif am.macd < 0 and am.lastmacd > 0 :
                fangxiang = kongping
            self.chulikaipingcang(fangxiang,price)


duo = 100
duoping = 50
paiduiduo = 150
paiduiduoping = 155
kong = 200
kongping = 250
paiduikong = 400
paiduikongping = 500
kaipantime = time(hour=9, minute=0)
zaoxiutime = time(hour=10,minute=15)
zaoxiuendtime = time(hour=10,minute=30)
shoupantime = time(hour=15,minute=0)
wuxiutime = time(hour=11,minute=30)
zhongwukaipantime = time(hour=13,minute=30)