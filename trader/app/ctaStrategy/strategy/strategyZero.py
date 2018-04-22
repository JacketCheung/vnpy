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
from vnpy.trader.app.dataRecorder.runDataCleaning import runDataCleaning
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

        #仓位相关
        self.posdetail = None

        #订单相关
        self.shortOrder = None
        self.buyOrder = None
        self.sellOrder = None
        self.coverOrder = None
        
    #----------------------------------------------------------------------
    def on30minBar(self, bar):
        """"""
        
        
    #----------------------------------------------------------------------
    def onInit(self):
        """初始化策略（必须由用户继承实现）"""
        self.writeCtaLog(u'%s策略初始化' %self.name)
        self.getPosDetail()
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
        self.writeCtaLog(yuanyin,'cancelorder')
        self.cancelOrder(order)
        if fangxiang == 'buy':
            self.buyOrder = None
        elif fangxiang == 'short':
            self.shortOrder = None
        elif fangxiang == 'sell':
            self.sellOrder == None
        elif fangxiang == 'cover':
            self.coverOrder = None
        else:
            self.writeCtaLog('ohmyghoa')
    #----------------------------------------------------------------------
    def buyTickCelve(self,tick):
        am = self.am
        fangxiang = None
        price = None
        if tick.datetime.second > 53:
            if am.diff > 0 and am.macd < 0 and am.lastmacd > 0:
                fangxiang = duo
                price = tick.bidPrice1

            elif am.macd > 0 and am.lastmacd < 0:
                    fangxiang = duoping
                    price = tick.askPrice1
            self.chulikaipingcang(fangxiang,price)


    #----------------------------------------------------------------------
    def shortTickCelve(self,tick):
        am = self.am
        fangxiang = None
        price = None
        if tick.datetime.second > 53:
            if am.diff < 0 and am.macd > 0 and am.lastmacd < 0:

                fangxiang = kong
                price = tick.askPrice1

            elif am.macd < 0 and am.lastmacd > 0:
                    fangxiang = kongping
                    price = tick.bidPrice1
            self.chulikaipingcang(fangxiang,price)

    #----------------------------------------------------------------------

    def onTick(self, tick):
        """收到行情TICK推送（必须由用户继承实现）"""
        self.bg.updateTick(tick)
        self.am.updateTick(tick)

        if not self.stopcount:
            self.buyTickCelve(tick)
            self.shortTickCelve(tick)
    def checkPingcang(self,bar):
        if self.didinited:
            am = self.am
            fangxiang = None
            price = None
            if self.posdetail.longPos > 0 and self.sellOrder is not None and am.lastmacd > 0 and am.mj < 0:
                self.cancelVtOrder(self.sellOrder, u'必须平多','sell')
                fangxiang = duoping
                price = am.tick.bidPrice1
            elif self.posdetail.shortPos > 0 and self.coverOrder is not None and am.lastmacd < 0 and am.mj > 0:
                self.cancelVtOrder(self.coverOrder, u'必须平空','cover')
                self.chulikaipingcang(kongping, am.tick.bidPrice1)
                fangxiang = kongping
                price = am.tick.askPrice1
            self.chulikaipingcang(fangxiang, price)
        #----------------------------------------------------------------------
    def getPosDetail(self):
        self.posdetail = self.ctaEngine.mainEngine.getPositionDetail(self.vtSymbol)

    def onBar(self, bar):
        """收到Bar推送（必须由用户继承实现）"""

         #检查是否有效的交易时间
        if self.notintradingTime(bar):
            runDataCleaning()
            return
        detail = self.posdetail
        print( detail.longPos,'long and short ',detail.shortPos )

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



    #----------------------------------------------------------------------
    def reactOrder(self,order,vtOrderID):
        print 'react',order.direction,order.offset

        if (order.direction == DIRECTION_LONG and order.offset == OFFSET_OPEN)                :
            print 'enterlong'
            self.buyOrder = vtOrderID
        elif  (order.direction == DIRECTION_SHORT and (order.offset == OFFSET_CLOSE or order.offset == OFFSET_CLOSETODAY or order.offset == OFFSET_CLOSEYESTERDAY)):
            print('entersell')
            self.sellOrder = vtOrderID
        elif    (order.direction == DIRECTION_SHORT and order.offset == OFFSET_OPEN):
            print 'entershort'
            self.shortOrder = vtOrderID
        elif (order.direction == DIRECTION_LONG and (
                order.offset == OFFSET_CLOSE or order.offset == OFFSET_CLOSETODAY or order.offset == OFFSET_CLOSEYESTERDAY)):
            print('enter coveer')
            self.coverOrder = vtOrderID
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
                if self.posdetail.longPos == 0 :
                    print  'buybuy'
                    self.orderBuy(price, 1)

            elif fangxiang == kong:
                if self.posdetail.shortPos ==  0  :
                    self.orderShort(price,1)

            elif fangxiang == duoping:
                if self.posdetail.longPos > 0 :
                    self.orderSell(price,1)
                if self.buyOrder is not None:
                    self.cancelVtOrder(self.buyOrder,u'平多时候','buy')


            elif fangxiang == kongping:
                if self.posdetail.shortPos > 0:
                    self.orderCover(price,1)
                if self.shortOrder is not None:
                    self.cancelVtOrder(self.shortOrder,u'平空时候','short')

        #-------------------------------------------------------
        '''订单管理类'''
    def orderBuy(self, price, volume = 1, stop=False):
            if self.buyOrder is None :
                self.buyOrder = 0
                self.buy(price,volume,stop)
    def orderSell(self, price, volume = 1, stop=False):
            if self.sellOrder is None:
                self.sellOrder = 0
                self.sell(price,volume,stop)

    def orderShort(self,price,volume = 1,stop = False):
            if self.shortOrder is None:
                self.shortOrder = 0
                self.short(price,volume,stop)
    def orderCover(self,price,volume = 1, stop = False):
            if self.coverOrder is None:
                self.coverOrder = 0
                self.cover(price,volume,stop)









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
        self.reSetOrder()
        self.stopcount = 20

    def notintradingTime(self, bar):
        dt = bar.datetime.time()
        if   ((MORNING_START <= dt < MORNING_REST) or
            (MORNING_RESTART <= dt < MORNING_END) or
            (AFTERNOON_START <= dt < AFTERNOON_END) or
            (dt >= NIGHT_START) or
            (dt < NIGHT_END)):
            return False
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
#回测用
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

    def reSetOrder(self):
        print '---------------------reset--------------'
        self.shortOrder = None
        self.coverOrder = None
        self.buyOrder = None
        self.sellOrder = None



duo = 100
duoping = 50
paiduiduo = 150
paiduiduoping = 155
kong = 200
kongping = 250
paiduikong = 400
paiduikongping = 500
MORNING_START = time(9, 0)
MORNING_REST = time(10, 16)
MORNING_RESTART = time(10, 30)
MORNING_END = time(11, 31)
AFTERNOON_START = time(13, 30)
AFTERNOON_END = time(15, 1)
NIGHT_START = time(21, 0)
NIGHT_END = time(2, 30)
NIGHT_START = time(21, 0)
NIGHT_END = time(2, 30)
