import datetime as dt
from decimal import Decimal
from typing import Dict, List, Optional, Any
from enum import Enum

from nautilus_trader.common.enums import LogColor
from nautilus_trader.indicators import MovingAverageFactory, MovingAverageType, RSI
from nautilus_trader.model.data import Bar, BarType, QuoteTick
from nautilus_trader.model.enums import OrderSide, PositionSide, OrderType, TimeInForce
from nautilus_trader.model.identifiers import InstrumentId, PositionId, OrderId
from nautilus_trader.model.objects import Money, Price, Quantity
from nautilus_trader.model.orders import MarketOrder, LimitOrder, StopMarketOrder, Order
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model.book import OrderBook
from BaseStrategyConfig import BaseStrategyConfig
from Intermediary.strategies.IStrategy import IndicatorStrategy


class BaseStrategy(Strategy, IndicatorStrategy):
    """
    基础交易策略 - 混合交易模式
    """

    def __init__(self, config: BaseStrategyConfig):
        """
        初始化策略

        参数:
            config: 完整配置对象
        """
        super().__init__(config)
        self.config = config

    def on_start(self):
        """策略启动生命周期事件"""
        self.start_time = dt.datetime.now()
        self.log.info(
            f"策略 {self.trader_id} 启动时间: {self.start_time}", color=LogColor.GREEN
        )
        # 注册指标指标在IndicatorStrategy，IndicatorStrategy的指标方法和方法体需要完善
        # .....
        # 订阅所有交易对的数据
        for instrument_id in self.config.instrument_ids:
            # 订阅K线数据
            self.subscribe_bars(bar_type)
            # 成交数据，只用于存在的订单订阅
            self.subscribe_trade_ticks(instrument_id)
            # 请求历史数据初始化指标
            # 需要根据传入的配置中的startup_candle_count来请求历史数据
            self.request_bars(
                bar_type,
                start=requests_start,
            )

    def on_order_book(self, order_book: OrderBook) -> None:
        """接收完整订单簿快照"""

    def on_bar(self, bar: Bar):
        """处理收到的K线数据"""
        # 判断所有指标是否加载完成
        # ...
        # 判断出场信号有一个满足并且有订单就出场
        # 出场需要调用IndicatorStrategy,方法体参数需要完善
        # ...
        # 判断入场信号，有一个满足就入场，但是不能有出场信号，如果满足出场信号则无视入场信号
        # 入场需要调用IndicatorStrategy,方法体参数需要完善
        # ...

    def on_historical_data(self, data) -> None:
        # 历史数据会自动更新注册的指标
        pass
