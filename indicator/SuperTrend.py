from nautilus_trader.core.correctness import PyCondition  
from nautilus_trader.indicators import Indicator  
from nautilus_trader.model.data import Bar  
from nautilus_trader.model.data import QuoteTick  
from nautilus_trader.model.data import TradeTick  
from nautilus_trader.model.enums import PriceType  
  
  
class SuperTrend(Indicator):  
    """  
    简化版SuperTrend指标，基于外部ATR值计算趋势方向。  
    只使用当前和前一根值进行对比，无需缓冲区。  
      
    参数  
    ----------  
    multiplier : float  
        ATR倍数，通常使用2.0或3.0  
    price_type : PriceType  
        从报价中提取价格的价格类型  
    """  
      
    def __init__(self, multiplier: float = 2.0, price_type: PriceType = PriceType.LAST):  
        PyCondition.positive(multiplier, "multiplier")  
          
        super().__init__(params=[multiplier])  
          
        self.multiplier = multiplier  
        self.price_type = price_type  
          
        # 只存储前一根的值  
        self._prev_hl2 = 0.0  
        self._prev_atr = 0.0  
        self._prev_upper_band = 0.0  
        self._prev_lower_band = 0.0  
        self._prev_close = 0.0  
        self._prev_trend = 0  
          
        # 当前值  
        self._current_hl2 = 0.0  
        self._current_atr = 0.0  
        self._upper_band = 0.0  
        self._lower_band = 0.0  
        self._trend = 0  
          
        # 输出值  
        self.value = 0.0  
        self.trend_direction = 0  
          
    def handle_quote_tick(self, tick: QuoteTick):  
        """处理报价tick数据"""  
        PyCondition.not_none(tick, "tick")  
        price = tick.extract_price(self.price_type)  
        self.update_raw(price.as_double(), 0.0)  
          
    def handle_trade_tick(self, tick: TradeTick):  
        """处理成交tick数据"""  
        PyCondition.not_none(tick, "tick")  
        self.update_raw(tick.price.as_double(), 0.0)  
          
    def handle_bar(self, bar: Bar):  
        """处理K线数据"""  
        PyCondition.not_none(bar, "bar")  
        hl2 = (bar.high.as_double() + bar.low.as_double()) / 2.0  
        self.update_raw(hl2, 0.0)  
          
    def update_with_atr(self, high: float, low: float, close: float, atr: float):  
        """使用OHLC数据和外部ATR值更新指标"""  
        hl2 = (high + low) / 2.0  
        self.update_raw(hl2, atr)  
          
    def update_raw(self, hl2: float, atr: float):  
        """使用HL2价格和ATR值更新指标"""  
        if not self.has_inputs:  
            self._set_has_inputs(True)  
            # 第一次输入，初始化  
            self._current_hl2 = hl2  
            self._current_atr = atr  
            self._prev_close = hl2  
            self._set_initialized(True)  
            return  
              
        # 保存前一根的值  
        self._prev_hl2 = self._current_hl2  
        self._prev_atr = self._current_atr  
        self._prev_upper_band = self._upper_band  
        self._prev_lower_band = self._lower_band  
        self._prev_trend = self._trend  
          
        # 更新当前值  
        self._current_hl2 = hl2  
        self._current_atr = atr  
          
        # 计算上下轨（使用当前值）  
        self._upper_band = self._current_hl2 + (self.multiplier * self._current_atr)  
        self._lower_band = self._current_hl2 - (self.multiplier * self._current_atr)  
          
        # 调整上下轨（避免频繁穿越）  
        if self._prev_upper_band != 0:  
            if self._upper_band < self._prev_upper_band or self._prev_close > self._prev_upper_band:  
                self._upper_band = self._prev_upper_band  
                  
        if self._prev_lower_band != 0:  
            if self._lower_band > self._prev_lower_band or self._prev_close < self._prev_lower_band:  
                self._lower_band = self._prev_lower_band  
          
        # 确定趋势方向  
        if self._current_hl2 <= self._upper_band:  
            self._trend = -1  # 下跌趋势  
        else:  
            self._trend = 1   # 上涨趋势  
              
        # 如果趋势改变，调整上下轨  
        if self._prev_trend != self._trend:  
            if self._trend == 1:  
                self._upper_band = self._current_hl2 + (self.multiplier * self._current_atr)  
            else:  
                self._lower_band = self._current_hl2 - (self.multiplier * self._current_atr)  
          
        # 设置输出值  
        if self._trend == 1:  
            self.value = self._lower_band  
        else:  
            self.value = self._upper_band  
              
        self.trend_direction = self._trend  
        self._prev_close = self._current_hl2  
          
    def _reset(self):  
        """重置指标状态"""  
        self._prev_hl2 = 0.0  
        self._prev_atr = 0.0  
        self._prev_upper_band = 0.0  
        self._prev_lower_band = 0.0  
        self._prev_close = 0.0  
        self._prev_trend = 0  
          
        self._current_hl2 = 0.0  
        self._current_atr = 0.0  
        self._upper_band = 0.0  
        self._lower_band = 0.0  
        self._trend = 0  
          
        self.value = 0.0  
        self.trend_direction = 0  
          
    @property  
    def upper_band(self) -> float:  
        """获取上轨值"""  
        return self._upper_band  
          
    @property  
    def lower_band(self) -> float:  
        """获取下轨值"""  
        return self._lower_band  
          
    @property  
    def is_uptrend(self) -> bool:  
        """是否为上涨趋势"""  
        return self._trend == 1  
          
    @property  
    def is_downtrend(self) -> bool:  
        """是否为下跌趋势"""  
        return self._trend == -1