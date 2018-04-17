# encoding: UTF-8

"""
本模块中主要包含：
1. 从通联数据下载历史行情的引擎
2. 用来把MultiCharts导出的历史数据载入到MongoDB中用的函数
3. 增加从通达信导出的历史数据载入到MongoDB中的函数
"""

from datetime import datetime, timedelta
from time import time

import pymongo

from vnpy.trader.vtGlobal import globalSetting
from vnpy.trader.vtConstant import *
from vnpy.trader.vtObject import VtBarData,VtTickData
from .ctaBase import SETTING_DB_NAME, TICK_DB_NAME, MINUTE_DB_NAME, DAILY_DB_NAME


#----------------------------------------------------------------------
def downloadEquityDailyBarts(self, symbol):
    """
    下载股票的日行情，symbol是股票代码
    """
    print u'开始下载%s日行情' %symbol
    
    # 查询数据库中已有数据的最后日期
    cl = self.dbClient[DAILY_DB_NAME][symbol]
    cx = cl.find(sort=[('datetime', pymongo.DESCENDING)])
    if cx.count():
        last = cx[0]
    else:
        last = ''
    # 开始下载数据
    import tushare as ts
    
    if last:
        start = last['date'][:4]+'-'+last['date'][4:6]+'-'+last['date'][6:]
        
    data = ts.get_k_data(symbol,start)
    
    if not data.empty:
        # 创建datetime索引
        self.dbClient[DAILY_DB_NAME][symbol].ensure_index([('datetime', pymongo.ASCENDING)], 
                                                            unique=True)                
        
        for index, d in data.iterrows():
            bar = VtBarData()
            bar.vtSymbol = symbol
            bar.symbol = symbol
            try:
                bar.open = d.get('open')
                bar.high = d.get('high')
                bar.low = d.get('low')
                bar.close = d.get('close')
                bar.date = d.get('date').replace('-', '')
                bar.time = ''
                bar.datetime = datetime.strptime(bar.date, '%Y%m%d')
                bar.volume = d.get('volume')
            except KeyError:
                print d
            
            flt = {'datetime': bar.datetime}
            self.dbClient[DAILY_DB_NAME][symbol].update_one(flt, {'$set':bar.__dict__}, upsert=True)            
        
        print u'%s下载完成' %symbol
    else:
        print u'找不到合约%s' %symbol

#----------------------------------------------------------------------
def loadMcCsv(fileName, dbName, symbol):
    """将Multicharts导出的csv格式的历史数据插入到Mongo数据库中"""
    import csv
    
    start = time()
    print u'开始读取CSV文件%s中的数据插入到%s的%s中' %(fileName, dbName, symbol)
    
    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort']) 
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)   
    
    # 读取数据和插入到数据库
    reader = csv.DictReader(file(fileName, 'r'))
    for d in reader:
        bar = VtBarData()
        bar.vtSymbol = symbol
        bar.symbol = symbol
        bar.open = float(d['Open'])
        bar.high = float(d['High'])
        bar.low = float(d['Low'])
        bar.close = float(d['Close'])
        bar.date = datetime.strptime(d['Date'], '%Y-%m-%d').strftime('%Y%m%d')
        bar.time = d['Time']
        bar.datetime = datetime.strptime(bar.date + ' ' + bar.time, '%Y%m%d %H:%M:%S')
        bar.volume = d['TotalVolume']

        flt = {'datetime': bar.datetime}
        collection.update_one(flt, {'$set':bar.__dict__}, upsert=True)  

    print u'插入完毕，耗时：%s' % (time()-start)

#----------------------------------------------------------------------
def loadTbCsv(fileName, dbName, symbol):
    """将TradeBlazer导出的csv格式的历史分钟数据插入到Mongo数据库中"""
    import csv
    
    start = time()
    print u'开始读取CSV文件%s中的数据插入到%s的%s中' %(fileName, dbName, symbol)
    
    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort'])
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)   
    
    # 读取数据和插入到数据库
    reader = csv.reader(file(fileName, 'r'))
    for d in reader:
        bar = VtBarData()
        bar.vtSymbol = symbol
        bar.symbol = symbol
        bar.open = float(d[1])
        bar.high = float(d[2])
        bar.low = float(d[3])
        bar.close = float(d[4])
        bar.date = datetime.strptime(d[0].split(' ')[0], '%Y/%m/%d').strftime('%Y%m%d')
        bar.time = d[0].split(' ')[1]+":00"
        bar.datetime = datetime.strptime(bar.date + ' ' + bar.time, '%Y%m%d %H:%M:%S')
        bar.volume = d[5]
        bar.openInterest = d[6]

        flt = {'datetime': bar.datetime}
        collection.update_one(flt, {'$set':bar.__dict__}, upsert=True)  
        print bar.date, bar.time
    
    print u'插入完毕，耗时：%s' % (time()-start)
    
 #----------------------------------------------------------------------
def loadTbPlusCsv(fileName, dbName, symbol):
    """将TB极速版导出的csv格式的历史分钟数据插入到Mongo数据库中"""
    import csv    

    start = time()
    print u'开始读取CSV文件%s中的数据插入到%s的%s中' %(fileName, dbName, symbol) 

    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort'])
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)      

    # 读取数据和插入到数据库
    reader = csv.reader(file(fileName, 'r'))
    for d in reader:
        bar = VtBarData()
        bar.vtSymbol = symbol
        bar.symbol = symbol
        bar.open = float(d[2])
        bar.high = float(d[3])
        bar.low = float(d[4])
        bar.close = float(d[5])
        bar.date = str(d[0])
        
        tempstr=str(round(float(d[1])*10000)).split(".")[0].zfill(4)
        bar.time = tempstr[:2]+":"+tempstr[2:4]+":00"
        
        bar.datetime = datetime.strptime(bar.date + ' ' + bar.time, '%Y%m%d %H:%M:%S')
        bar.volume = d[6]
        bar.openInterest = d[7]
        flt = {'datetime': bar.datetime}
        collection.update_one(flt, {'$set':bar.__dict__}, upsert=True)
        print bar.date, bar.time    

    print u'插入完毕，耗时：%s' % (time()-start)

#----------------------------------------------------------------------
def loadTdxCsv(fileName, dbName, symbol):
    """将通达信导出的csv格式的历史分钟数据插入到Mongo数据库中"""
    import csv
    
    start = time()
    print u'开始读取CSV文件%s中的数据插入到%s的%s中' %(fileName, dbName, symbol)
    
    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort'])
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)   
    
    # 读取数据和插入到数据库
    reader = csv.reader(file(fileName, 'r'))
    for d in reader:
        bar = VtBarData()
        bar.vtSymbol = symbol
        bar.symbol = symbol
        bar.open = float(d[2])
        bar.high = float(d[3])
        bar.low = float(d[4])
        bar.close = float(d[5])
        bar.date = datetime.strptime(d[0], '%Y/%m/%d').strftime('%Y%m%d')
        bar.time = d[1][:2]+':'+d[1][2:4]+':00'
        bar.datetime = datetime.strptime(bar.date + ' ' + bar.time, '%Y%m%d %H:%M:%S')
        bar.volume = d[6]
        bar.openInterest = d[7]

        flt = {'datetime': bar.datetime}
        collection.update_one(flt, {'$set':bar.__dict__}, upsert=True)  
        print bar.date, bar.time
    
    print u'插入完毕，耗时：%s' % (time()-start)
#-----------------------------------------------------

def loadqlCsv(fileName, dbName, symbol):
    """将TB极速版导出的csv格式的历史分钟数据插入到Mongo数据库中"""
    import csv
    count = 0
    start = time()
    print u'开始读取CSV文件%s中的数据插入到%s的%s中' % (fileName, dbName, symbol)

    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort'])
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)

    # 读取数据和插入到数据库
    reader = csv.reader(file(fileName, 'r'))
    for d in reader:
        tick = VtTickData()
        tick.vtSymbol = symbol
        tick.symbol = symbol
        tick.lastPrice = float(d[5])
        tick.volume = int(d[6])
        tick.openPrice = float(d[9])
        tick.highPrice = float(d[7])
        tick.lowPrice = float(d[8])
        tick.preClosePrice = float(d[20])
        tick.askPrice1 = float(d[12])
        tick.bidPrice1 = float(d[14])
        tick.askVolume1 = float(d[13])
        tick.bidVolume1 = float(d[15])
        count += 1


        tick.date = datetime.strptime(d[2], '%Y%m%d').strftime('%Y%m%d')

        if d[4] == '500':
            tick.time = d[3] + "." + "500000"
        else:
            tick.time = d[3] + "." + "000000"
        tick.datetime = datetime.strptime(tick.date + ' ' + tick.time, '%Y%m%d %H:%M:%S.%f')
        flt = {'datetime': tick.datetime}
        collection.update_one(flt, {'$set': tick.__dict__}, upsert=True)

    print u'插入完毕，耗时：%s插入数量' % (time() - start),count

def load13Csv(fileName, dbName, symbol):
    """将TB极速版导出的csv格式的历史分钟数据插入到Mongo数据库中"""
    import csv
    count = 0
    start = time()
    print u'开始读取CSV文件%s中的数据插入到%s的%s中' % (fileName, dbName, symbol)

    # 锁定集合，并创建索引
    client = pymongo.MongoClient(globalSetting['mongoHost'], globalSetting['mongoPort'])
    collection = client[dbName][symbol]
    collection.ensure_index([('datetime', pymongo.ASCENDING)], unique=True)

    # 读取数据和插入到数据库
    reader = csv.reader(file(fileName, 'r'))
    lasttime = None
    for d in reader:
        tick = VtTickData()
        tick.vtSymbol = symbol
        tick.symbol = symbol
        tick.lastPrice = float(d[2])
        tick.volume = int(d[6])
        tick.askPrice1 = float(d[3])
        tick.bidPrice1 = float(d[4])
        count += 1


        zhongjian = datetime.strptime(d[0], '%Y-%m-%d')
        tick.date = zhongjian.strftime('%Y%m%d')

        if d[1] == lasttime:
            tick.time = d[1] + "." + "500000"
        else:
            tick.time = d[1] + "." + "000000"
        lasttime = d[1]
        tick.datetime = datetime.strptime(tick.date + ' ' + tick.time, '%Y%m%d %H:%M:%S.%f')
        flt = {'datetime': tick.datetime}
        collection.update_one(flt, {'$set': tick.__dict__}, upsert=True)

    print u'插入完毕，耗时：%s插入数量' % (time() - start),count
