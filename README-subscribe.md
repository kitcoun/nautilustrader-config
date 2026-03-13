## 所有订阅方法

NautilusTrader提供了多种数据订阅方法 nautilus_trader:192-201 ：

### 市场数据订阅
- `subscribe_quote_ticks()` - 订阅报价数据 nautilus_trader:192-192 
- `subscribe_trade_ticks()` - 订阅成交数据 nautilus_trader:193-193 
- `subscribe_bars()` - 订阅K线数据 nautilus_trader:197-197 
- `subscribe_mark_prices()` - 订阅标记价格 nautilus_trader:194-194 
- `subscribe_index_prices()` - 订阅指数价格 nautilus_trader:195-195 
- `subscribe_funding_rates()` - 订阅资金费率 nautilus_trader:196-196 

### 订单簿数据订阅
- `subscribe_order_book_deltas()` - 订阅订单簿增量数据 nautilus_trader:183-183 
- `subscribe_order_book_depth()` - 订阅订单簿深度数据 nautilus_trader:185-185 
- `subscribe_order_book_at_interval()` - 订阅定时订单簿快照 nautilus_trader:187-187 

### 合约和状态订阅
- `subscribe_instruments()` - 订阅合约信息 nautilus_trader:181-181 
- `subscribe_instrument_status()` - 订阅合约状态 nautilus_trader:198-198 
- `subscribe_instrument_close()` - 订阅合约收盘信息 nautilus_trader:199-199 
- `subscribe_option_greeks()` - 订阅期权希腊字母 nautilus_trader:200-200 
- `subscribe_option_chain()` - 订阅期权链 nautilus_trader:201-201 

### 订单事件订阅
- `subscribe_order_fills()` - 订阅订单成交事件 nautilus_trader:202-202 
- `subscribe_order_cancels()` - 订阅订单取消事件 nautilus_trader:203-203 

## 对应的取消订阅方法

每个订阅方法都有对应的取消订阅方法，如 `unsubscribe_quote_ticks()`、`unsubscribe_trade_ticks()` 等 nautilus_trader:210-219 。

## Notes

- 订阅方法通常在 `on_start()` 生命周期方法中调用
- 实时数据通过相应的回调方法（如 `on_quote_tick()`）接收
- 历史数据通过 `request_*()` 方法请求，通过 `on_historical_data()` 接收
- 不同交易所适配器可能对某些数据类型有不同支持程度

Wiki pages you might want to explore:
- [Component Lifecycle and State Machine (nautechsystems/nautilus_trader)](/wiki/nautechsystems/nautilus_trader#2.9)
### Citations
**File:** docs/concepts/actors.md (L150-151)
```markdown
| `subscribe_quote_ticks()`            | Real-time  | `on_quote_tick()`        | Live quote updates.                               |
| `subscribe_trade_ticks()`            | Real-time  | `on_trade_tick()`        | Live trade updates.                               |
```
**File:** nautilus_trader/common/actor.pxd (L181-181)
```text
        dict[str, object] params=*,
```
**File:** nautilus_trader/common/actor.pxd (L183-183)
```text
    cpdef void subscribe_order_book_at_interval(
```
**File:** nautilus_trader/common/actor.pxd (L185-185)
```text
        InstrumentId instrument_id,
```
**File:** nautilus_trader/common/actor.pxd (L187-187)
```text
        int depth=*,
```
**File:** nautilus_trader/common/actor.pxd (L192-201)
```text
    cpdef void subscribe_quote_ticks(self, InstrumentId instrument_id, ClientId client_id=*, bint update_catalog=*, bint aggregate_spread_quotes=*, dict[str, object] params=*)
    cpdef void subscribe_trade_ticks(self, InstrumentId instrument_id, ClientId client_id=*, bint update_catalog=*, dict[str, object] params=*)
    cpdef void subscribe_mark_prices(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void subscribe_index_prices(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void subscribe_funding_rates(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void subscribe_bars(self, BarType bar_type, ClientId client_id=*, bint update_catalog=*, dict[str, object] params=*)
    cpdef void subscribe_instrument_status(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void subscribe_instrument_close(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void subscribe_option_greeks(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void subscribe_option_chain(self, object series_id, object strike_range=*, object snapshot_interval_ms=*, ClientId client_id=*, dict[str, object] params=*)
```
**File:** nautilus_trader/common/actor.pxd (L202-202)
```text
    cpdef void subscribe_order_fills(self, InstrumentId instrument_id)
```
**File:** nautilus_trader/common/actor.pxd (L203-203)
```text
    cpdef void subscribe_order_cancels(self, InstrumentId instrument_id)
```
**File:** nautilus_trader/common/actor.pxd (L210-219)
```text
    cpdef void unsubscribe_quote_ticks(self, InstrumentId instrument_id, ClientId client_id=*, bint aggregate_spread_quotes=*, dict[str, object] params=*)
    cpdef void unsubscribe_trade_ticks(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_mark_prices(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_index_prices(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_funding_rates(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_bars(self, BarType bar_type, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_instrument_status(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_instrument_close(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_option_greeks(self, InstrumentId instrument_id, ClientId client_id=*, dict[str, object] params=*)
    cpdef void unsubscribe_option_chain(self, object series_id, ClientId client_id=*, dict[str, object] params=*)
```
## Q5
subscribe_quote_ticks 这个是什么意思呢？有那些这种方法呢？
*Codemap generation in progress or failed to parse*