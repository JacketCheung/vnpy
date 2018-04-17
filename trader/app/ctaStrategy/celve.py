
class celvemoban(object):
    # 100 代表多开，50 代表多平，200代表空开，250代表空平
    def __init__(self):
        self.cangwei = 0
        self.caozuo = 0
        self.chicangjia = None
        self.tickadd = 1
    def cangweishibie(self,caozuo):
        if self.cangwei == 0 and caozuo == 100:
            self.cangwei += 1
            print 'return 100'
            return 100
        elif self.cangwei == 1 and caozuo == 50:
            self.cangwei -= 1
            print 'retr 50'
            return 50
        else:
            print 'ekse',self.cangwei,caozuo
            return 0
########################################################################
class gongzhencelve(celvemoban):
     def zuoduocelve(self,bar1m,bar3m,bar5m,bar15m,lastprice):
         caozuo = 0
         duo = 100
         if bar1m.lastbar.macd<0 and bar1m.macd > 0 and bar15m.mj > 0:
                 if bar3m.lastbar.macd < 0:
                     if bar3m.macd > 0:
                         if bar5m.mj > 0 and bar5m.macd > bar5m.lowestMACD * 1/3:
                             caozuo = duo
                         else: caozuo = 0
                     else:
                         if bar3m.mj > 0 :
                             bar3m.caculateMACD(lastprice + 3 * self.tickadd)
                             bar5m.caculateMACD(lastprice + 5 * self.tickadd)
                             if bar3m.macd > 0 and bar5m.macd > 0 and bar5m.mj > 0:
                                 caozuo = duo
                             bar3m.caculateMACD(lastprice )
                             bar5m.caculateMACD(lastprice )
                 else:#bar3m.lastbar.macd > 0
                     if bar5m.mj > 0 and (bar5m.macd > 0 or bar5m.macd > bar5m.lowestMACD * 1/3):
                         caozuo = duo

         return  self.cangweishibie(caozuo)



     def zuokongcelve(self,bar1m,bar3m,bar5m,bar15m,lastprice):
         caozuo = 0
         duo = 200
         if bar1m.lastbar.macd > 0 and bar1m.macd < 0 and bar15m.mj < 0:
             if bar3m.lastbar.macd > 0:
                 if bar3m.macd < 0:
                     if bar5m.mj < 0 and bar5m.macd < bar5m.hightestMACD * 1 / 3:
                         caozuo = duo
                     else:
                         caozuo = 0
                 else:
                     if bar3m.mj < 0:
                         bar3m.caculateMACD(lastprice - 3 * self.tickadd)
                         bar5m.caculateMACD(lastprice - 5 * self.tickadd)
                         if bar3m.macd < 0 and bar5m.macd < 0 and bar5m.mj < 0:
                             caozuo = duo
                         bar3m.caculateMACD(lastprice)
                         bar5m.caculateMACD(lastprice)
             else:  # bar3m.lastbar.macd < 0
                 if bar5m.mj < 0 and (bar5m.macd < 0 or bar5m.macd < bar5m.hightestMACD * 1 / 3):
                     caozuo = duo
         return self.cangweishibie(caozuo)
     def celve(self,bar1m,bar3m,bar5m,bar15m,lastprice):
        caozuo = 0
        if not self.cangwei:
            if bar1m.macd>0:
               caozuo = self.zuoduocelve(bar1m,bar3m,bar5m,bar15m,lastprice)
            else:
               caozuo = self.zuokongcelve(bar1m,bar3m,bar5m,bar15m,lastprice)
        elif self.cangwei == 1:
            if bar.diff - bar.lastbar.diff <0:
                caozuo = 50
        elif self.cangwei == -1:
            if bar.diff - bar.lastbar.diff > 0:
                caozuo = 250
        return self.cangweishibie(caozuo)


########################################################################
class lianmiancelve(celvemoban):
    def __init__(self):
        super(lianmiancelve, self).__init__()
        self.minute =0
        self.lowestMACD  = None
        self.lowprice = None
        self.count = 0
        self.highprice = None
        self.begin = False
        self.tiaojianjubei = False
    def kongcelveOnbar(self,bar):
        if bar.macd < 0 :
            if bar.mj > 0 and bar.lastbar.mj < 0 :
                if self.lowestMACD is None or self.lowprice is None:
                    self.tiaojianjubei = True
                    self.lowestMACD = bar.macd
                    self.lowprice = bar.low
                    self.highprice = bar.high
                elif bar.lastbar.macd < self.lowestMACD and bar.lastbar.close < self.lowprice:
                    self.lowestMACD = bar.lastbar.macd
                    self.lowprice = bar.lastbar.low
                    self.highprice = bar.high
                    self.tiaojianjubei = True
            if self.lowestMACD is not None and self.highprice is not None:
                if bar.high > self.highprice + 2 * self.tickadd:
                    self.tiaojianjubei = False
        elif not (self.tiaojianjubei and bar.high < self.highprice + 2 * self.tickadd):
            self.tiaojianjubei = False
            self.lowestMACD = None
            self.lowprice = None
            self.highprice = None
            self.secondbar = None
    def celve(self,bar,lastbar,tick):
        # 这里以后需要加上大周期的观察
        caozuo = 0
        if not self.cangwei:
            if self.minute != tick.datetime.minute:
                self.minute = tick.datetime.minute
                self.count = 0
            else:
                if bar.macd < 0  and self.tiaojianjubei == True and bar.mj < 0 and bar.lastbar.macd > self.lowestMACD * 1.0/3.0  and bar.diff < 0.5:
                    self.count += 1
                    if self.count > 5:
                        caozuo = 200
                        self.count = 0
        elif  bar.diff - bar.lastbar.diff > 0 and tick.lastPrice != self.chicangjia + 2 * self.tickadd and tick.lastPrice !=  self.chicangjia + self.tickadd and tick.lastPrice != self.chicangjia:
                caozuo = 250
        ######ceshi
        caozuo = 100
        return  self.cangweishibie(caozuo)

class zerocelve(celvemoban):
    def celve(self,bar,refbar,tick):
        caozuo = 0
        if not self.cangwei:
            canshu = 0.12
            if refbar is not None and refbar.diff < canshu and refbar.diff > -canshu and refbar.dea < canshu and refbar.dea > -canshu and refbar.macd < 0\
                              and bar.diff - refbar.diff > 0 :
                if  bar.macd > 0:
                    caozuo = 100
                else :
                    bar.caculateMACD(bar.close + 1)
                    if bar.macd > 0:
                        caozuo = 100
                    else:
                        caozuo = 0
                    bar.caculateMACD(bar.close)
        elif bar.diff - refbar.diff < 0:
            caozuo = 50
        return self.cangweishibie(caozuo)
class testcelve(celvemoban):
    def celve(self,bar):
        caozuo = 0
        if not self.cangwei:
            caozuo = 100
        else:
            caozuo = 0
        return self.cangweishibie(caozuo)