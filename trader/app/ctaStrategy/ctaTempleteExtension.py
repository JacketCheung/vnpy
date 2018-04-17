from ctaTemplate import ArrayManager

class zhibiao(ArrayManager):
    def __init__(self, lastshort= 0,lastlong = 0,lastdea = 0,size=100):
        super(zhibiao,self).__init__(lastshort,lastlong,lastdea,size)
        self.langshu = 0

        self.datetime = None

        self.tick = None

        self.diff = 0
        self.dea = 0
        self.short = 0
        self.long = 0
        self.macd = 0
        self.mj = 0

        self.lastdiff = 0
        self.lastdea = lastdea
        self.lastshort = lastshort
        self.lastlong = lastlong
        self.lastmacd = 0
        self.lastmj = 0

        self.redWaveCount = 0
        self.greendWaveCount = 0
        self.lastRedWaveCount = 0
        self.lastGreenWaveCount = 0
        self.waveCounts = 0

    def inred(self):
        return self.macd > 0
    def updateBar(self, bar):
        super(zhibiao,self).updateBar(bar)

        self.caculateMACD(bar.close)
        self.datetime = bar.datetime

        self.countWave()
    def caculateEMA(self, price, lastEMA, alpha=2.0 / 13.0):
        return alpha * price + (1 - alpha) * lastEMA

    def updateTick(self, tick):
        self.caculateMACD(tick.lastPrice)
        self.close[-1] = tick.lastPrice
        self.tick = tick
    def caculateMACD(self, lastPrice):
        if self.lastshort == 0 and self.lastlong == 0:
            self.short = lastPrice
            self.long = lastPrice
        else:
            self.short = self.caculateEMA(lastPrice, self.lastshort)
            self.long = self.caculateEMA(lastPrice, self.lastlong, 2.0 / 27.0)
        self.diff = self.short - self.long
        self.dea = self.caculateEMA(self.diff, self.lastdea, 0.2)
        self.macd = 2 * (self.diff - self.dea)
        self.mj = self.macd - self.lastmacd

    def newprice(self, lastPrice):
        self.caculateMACD(lastPrice)

    def endBar(self):
        self.lastshort = self.short
        self.lastdea = self.dea
        self.lastdiff = self.diff
        self.lastlong = self.long
        self.lastmacd = self.macd
        self.lastmj = self.mj

    # print('endbar,and short is ',self.short,'diffis',self.diff,'lastshort is',self.lastshort)
    def dj(self):
        return self.diff - self.lastdiff

    def countWave(self):
        if self.macd >0 and self.lastmacd < 0:
            self.lastRedWaveCount = self.redWaveCount
            self.redWaveCount = 1
            self.waveCounts += 1
        elif self.macd < 0 and self.lastmacd > 0:
            self.lastGreenWaveCount = self.greendWaveCount
            self.greendWaveCount = 1
            self.waveCounts += 1
        elif self.macd <0 and self.lastmacd < 0:
            self.greendWaveCount += 1
        elif self.macd >0 and self.lastmacd >0:
            self.redWaveCount += 1