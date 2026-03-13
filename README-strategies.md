```python
Strategy 可重写方法（带中文注释）
1. 生命周期方法
这些方法在策略生命周期状态变化时触发 strategies.md:80-95 ：

def on_start(self) -> None:  
    """策略启动时调用 - 用于初始化策略（如获取合约、订阅数据）"""  
      
def on_stop(self) -> None:  
    """策略停止时调用 - 用于清理任务（如取消未成交订单、平仓、取消订阅）"""  
      
def on_resume(self) -> None:  
    """策略恢复时调用 - 在停止后重新启动时执行"""  
      
def on_reset(self) -> None:  
    """策略重置时调用 - 重置策略状态和指标"""  
      
def on_dispose(self) -> None:  
    """策略销毁时调用 - 释放资源"""  
      
def on_degrade(self) -> None:  
    """策略降级时调用 - 处理性能降级情况"""  
      
def on_fault(self) -> None:  
    """策略故障时调用 - 处理错误情况"""  
      
def on_save(self) -> dict[str, bytes]:  
    """保存策略状态时调用 - 返回用户定义的状态字典"""  
      
def on_load(self, state: dict[str, bytes]) -> None:  
    """加载策略状态时调用 - 从保存的状态恢复策略"""
2. 数据处理方法
接收市场数据更新 strategies.md:102-120 ：

def on_order_book_deltas(self, deltas: OrderBookDeltas) -> None:  
    """接收订单簿增量更新"""  
      
def on_order_book(self, order_book: OrderBook) -> None:  
    """接收完整订单簿快照"""  
      
def on_quote_tick(self, tick: QuoteTick) -> None:  
    """接收报价行情数据"""  
      
def on_trade_tick(self, tick: TradeTick) -> None:  
    """接收成交行情数据"""  
      
def on_bar(self, bar: Bar) -> None:  
    """接收K线数据"""  
      
def on_instrument(self, instrument: Instrument) -> None:  
    """接收合约信息"""  
      
def on_instrument_status(self, status: InstrumentStatus) -> None:  
    """接收合约状态更新"""  
      
def on_instrument_close(self, close: InstrumentClose) -> None:  
    """接收合约关闭通知"""  
      
def on_option_chain_slice(self, slice: OptionChainSlice) -> None:  
    """接收期权链切片数据"""  
      
def on_option_greeks(self, greeks: OptionGreeks) -> None:  
    """接收期权希腊字母数据"""
3. 订单事件处理器
处理订单生命周期事件 strategy.pxd:113-133 ：

def on_order_event(self, event: OrderEvent) -> None:  
    """通用订单事件处理器 - 所有订单事件最终都会传递到此方法"""  
      
def on_order_initialized(self, event: OrderInitialized) -> None:  
    """订单初始化时调用"""  
      
def on_order_denied(self, event: OrderDenied) -> None:  
    """订单被拒绝时调用（风控拒绝）"""  
      
def on_order_emulated(self, event: OrderEmulated) -> None:  
    """订单被模拟时调用"""  
      
def on_order_released(self, event: OrderReleased) -> None:  
    """订单释放时调用"""  
      
def on_order_submitted(self, event: OrderSubmitted) -> None:  
    """订单提交到交易所时调用"""  
      
def on_order_rejected(self, event: OrderRejected) -> None:  
    """订单被交易所拒绝时调用"""  
      
def on_order_accepted(self, event: OrderAccepted) -> None:  
    """订单被交易所接受时调用"""  
      
def on_order_canceled(self, event: OrderCanceled) -> None:  
    """订单被取消时调用"""  
      
def on_order_expired(self, event: OrderExpired) -> None:  
    """订单过期时调用"""  
      
def on_order_triggered(self, event: OrderTriggered) -> None:  
    """订单被触发时调用（如止损单）"""  
      
def on_order_pending_update(self, event: OrderPendingUpdate) -> None:  
    """订单待更新时调用"""  
      
def on_order_pending_cancel(self, event: OrderPendingCancel) -> None:  
    """订单待取消时调用"""  
      
def on_order_modify_rejected(self, event: OrderModifyRejected) -> None:  
    """订单修改被拒绝时调用"""  
      
def on_order_cancel_rejected(self, event: OrderCancelRejected) -> None:  
    """订单取消被拒绝时调用"""  
      
def on_order_updated(self, event: OrderUpdated) -> None:  
    """订单更新时调用"""  
      
def on_order_filled(self, event: OrderFilled) -> None:  
    """订单成交时调用"""
4. 持仓事件处理器
处理持仓状态变化 strategy.pxd:130-134 ：

def on_position_event(self, event: PositionEvent) -> None:  
    """通用持仓事件处理器 - 所有持仓事件最终都会传递到此方法"""  
      
def on_position_opened(self, event: PositionOpened) -> None:  
    """持仓开启时调用"""  
      
def on_position_changed(self, event: PositionChanged) -> None:  
    """持仓变化时调用（如部分平仓）"""  
      
def on_position_closed(self, event: PositionClosed) -> None:  
    """持仓关闭时调用"""
5. 市场退出钩子
处理市场退出流程 strategy.pxd:111-112 ：

def on_market_exit(self) -> None:  
    """市场退出前调用 - 执行退出前的准备工作"""  
      
def post_market_exit(self) -> None:  
    """市场退出后调用 - 执行退出后的清理工作"""
6. 通用事件处理器
def on_event(self, event: Event) -> None:  
    """通用事件处理器 - 接收所有到达策略的事件"""
```