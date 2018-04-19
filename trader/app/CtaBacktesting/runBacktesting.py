# encoding: UTF-8

"""
展示如何执行策略回测。
"""

from __future__ import division


from vnpy.trader.app.ctaStrategy.ctaBacktesting import BacktestingEngine, MINUTE_DB_NAME


if __name__ == '__main__':
    from vnpy.trader.app.ctaStrategy.strategy.strategyDoubleMa import DoubleMaStrategy
    
    # 创建回测引擎
    engine = BacktestingEngine()
    
    # 设置引擎的回测模式为K线
    engine.setBacktestingMode(engine.BAR_MODE)

    # 设置回测用的数据起始日期
    engine.setStartDate('20120721')
    
    # 设置产品相关参数
    engine.setSlippage(1)     # 股指1跳
    engine.setRate(0.3/10000)   # 万0.3
    engine.setSize(10)         # 股指合约大小
    engine.setPriceTick(1)    # 股指最小价格变动
    
    # 设置使用的历史数据库
    engine.setDatabase(MINUTE_DB_NAME, 'rb0000')
    
    # 在引擎中创建策略对象
    d = {}
    engine.initStrategy(DoubleeMaStraty, d)
    
    # 开始跑回测
    engine.runBacktesting()
    
    # 显示回测结果
    engine.showBacktestingResult()