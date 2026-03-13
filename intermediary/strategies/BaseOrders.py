from decimal import Decimal
from typing import Any

import pandas as pd

from nautilus_trader.model.enums import OrderSide
from nautilus_trader.model.enums import OrderType
from nautilus_trader.model.enums import TimeInForce
from nautilus_trader.model.enums import TriggerType
from nautilus_trader.model.instruments import Instrument
from nautilus_trader.model.objects import Price
from nautilus_trader.model.objects import Quantity
from nautilus_trader.model.orders import LimitIfTouchedOrder
from nautilus_trader.model.orders import LimitOrder
from nautilus_trader.model.orders import MarketIfTouchedOrder
from nautilus_trader.model.orders import MarketOrder
from nautilus_trader.model.orders import Order
from nautilus_trader.model.orders import StopLimitOrder
from nautilus_trader.model.orders import StopMarketOrder
from nautilus_trader.model.orders import TrailingStopMarketOrder

class BaseOrders:
    def __init__(self):
        self.orders = []

    def maintain_orders(self, best_bid: Price, best_ask: Price) -> None:
        """
        根据当前最优买卖盘维护订单（创建、修改或撤单）。
        """
        if self.instrument is None or self.config.dry_run or self.is_exiting():
            return

        if self.config.enable_limit_buys:
            self.maintain_buy_orders(self.instrument, best_bid, best_ask)

        if self.config.enable_limit_sells:
            self.maintain_sell_orders(self.instrument, best_bid, best_ask)

        if self.config.enable_stop_buys:
            self.maintain_stop_buy_orders(self.instrument, best_bid, best_ask)

        if self.config.enable_stop_sells:
            self.maintain_stop_sell_orders(self.instrument, best_bid, best_ask)

    def maintain_buy_orders(
        self,
        instrument: Instrument,
        best_bid: Price,
        best_ask: Price,
    ) -> None:
        """
        维护限价买单：计算目标价格，如果无活跃买单则创建，否则根据需要修改或撤单重下。
        """
        # 目标价格 = 最优买价 - 偏移量
        price = instrument.make_price(best_bid - self.price_offset)

        if self.config.enable_brackets:
            # 如果启用括号订单，则提交括号订单（入场单+止盈止损）
            if not self.buy_order or not self.is_order_active(self.buy_order):
                self.submit_bracket_order(OrderSide.BUY, price)
            return

        # 无活跃买单时提交新单
        if not self.buy_order or not self.is_order_active(self.buy_order):
            if self.config.use_post_only and self.config.test_reject_post_only:
                # 故意将价格设在ask上方以触发post-only拒绝（测试场景）
                price = instrument.make_price(best_ask + self.price_offset)

            self.submit_limit_order(OrderSide.BUY, price)
        elif (
            self.buy_order
            and self.buy_order.venue_order_id
            and not self.buy_order.is_pending_update
            and not self.buy_order.is_pending_cancel
            and self.buy_order.price < price
        ):
            # 当前买单价格低于目标价格（市场上涨），需要上移价格
            if self.config.modify_orders_to_maintain_tob_offset:
                self.modify_order(self.buy_order, price=price)
            elif self.config.cancel_replace_orders_to_maintain_tob_offset:
                self.cancel_order(self.buy_order)
                self.submit_limit_order(OrderSide.BUY, price)

    def maintain_sell_orders(
        self,
        instrument: Instrument,
        best_bid: Price,
        best_ask: Price,
    ) -> None:
        """
        维护限价卖单：目标价格 = 最优卖价 + 偏移量。
        """
        price = instrument.make_price(best_ask + self.price_offset)

        if self.config.enable_brackets:
            if not self.sell_order or not self.is_order_active(self.sell_order):
                self.submit_bracket_order(OrderSide.SELL, price)
            return

        if not self.sell_order or not self.is_order_active(self.sell_order):
            if self.config.use_post_only and self.config.test_reject_post_only:
                price = instrument.make_price(best_bid - self.price_offset)

            self.submit_limit_order(OrderSide.SELL, price)
        elif (
            self.sell_order
            and self.sell_order.venue_order_id
            and not self.sell_order.is_pending_update
            and not self.sell_order.is_pending_cancel
            and self.sell_order.price > price
        ):
            # 当前卖单价格高于目标价格（市场下跌），需要下移价格
            if self.config.modify_orders_to_maintain_tob_offset:
                self.modify_order(self.sell_order, price=price)
            elif self.config.cancel_replace_orders_to_maintain_tob_offset:
                self.cancel_order(self.sell_order)
                self.submit_limit_order(OrderSide.SELL, price)

    def open_position(self, net_qty: Decimal) -> None:
        """
        开仓：提交市价单。
        net_qty > 0 表示多头，< 0 表示空头。
        """
        if not self.instrument:
            self.log.error("No instrument loaded")
            return

        if net_qty == Decimal(0):
            self.log.warning(f"Open position with {net_qty}, skipping")
            return

        quantity = self.instrument.make_qty(abs(net_qty))

        order: MarketOrder = self.order_factory.market(
            instrument_id=self.config.instrument_id,
            order_side=OrderSide.BUY if net_qty > 0 else OrderSide.SELL,
            quantity=quantity,
            time_in_force=self.config.open_position_time_in_force,
            quote_quantity=self.config.use_quote_quantity,
            reduce_only=self.config.test_reject_reduce_only,  # 测试reduce-only拒绝
        )

        self.submit_order(
            order,
            client_id=self.client_id,
            params=self.config.order_params,
        )

    def get_price_offset(self, instrument: Instrument) -> Decimal:
        """计算价格偏移量（tick数 * 价格增量）"""
        return instrument.price_increment * self.config.tob_offset_ticks

    def is_order_active(self, order: Order) -> bool:
        """判断订单是否处于活跃状态（本地活跃、飞行中或开放）"""
        return order.is_active_local or order.is_inflight or order.is_open

    def _resolve_time_in_force(
        self,
        tif_override: TimeInForce | None,
    ) -> tuple[TimeInForce, pd.Timestamp | None]:
        """
        根据配置和传入的tif_override解析最终的有效期和过期时间。
        返回 (time_in_force, expire_time)
        """
        if tif_override == TimeInForce.GTD:
            if self.config.order_expire_time_delta_mins is not None:
                expire_time = self.clock.utc_now() + pd.Timedelta(
                    minutes=self.config.order_expire_time_delta_mins,
                )
                return TimeInForce.GTD, expire_time
            self.log.warning(
                "GTD time in force requires order_expire_time_delta_mins, falling back to GTC",
            )
            return TimeInForce.GTC, None
        if tif_override is not None:
            return tif_override, None
        if self.config.order_expire_time_delta_mins is not None:
            expire_time = self.clock.utc_now() + pd.Timedelta(
                minutes=self.config.order_expire_time_delta_mins,
            )
            return TimeInForce.GTD, expire_time
        return TimeInForce.GTC, None

    def submit_limit_order(self, order_side: OrderSide, price: Price) -> None:
        """
        提交限价单。
        """
        if not self.instrument:
            self.log.error("No instrument loaded")
            return

        if self.config.dry_run:
            self.log.warning(f"Dry run, skipping create {order_side} order")
            return

        if order_side == OrderSide.BUY and not self.config.enable_limit_buys:
            self.log.warning("BUY orders not enabled, skipping")
            return
        elif order_side == OrderSide.SELL and not self.config.enable_limit_sells:
            self.log.warning("SELL orders not enabled, skipping")
            return

        if self.config.enable_brackets:
            self.submit_bracket_order(order_side, price)
            return

        time_in_force, expire_time = self._resolve_time_in_force(
            self.config.limit_time_in_force,
        )

        if self.config.order_display_qty is not None:
            # 如果设置了显示数量，则为冰山订单；若为0，则为隐藏订单
            display_qty = self.instrument.make_qty(self.config.order_display_qty)
        else:
            display_qty = None

        # 解析模拟触发类型（可能为字符串，需转换为枚举）
        emulation_trigger = (
            TriggerType[self.config.emulation_trigger]
            if isinstance(self.config.emulation_trigger, str)
            else (self.config.emulation_trigger or TriggerType.NO_TRIGGER)
        )

        order: LimitOrder = self.order_factory.limit(
            instrument_id=self.config.instrument_id,
            order_side=order_side,
            quantity=self.instrument.make_qty(self.config.order_qty),
            price=price,
            time_in_force=time_in_force,
            expire_time=expire_time,
            post_only=self.config.use_post_only,
            quote_quantity=self.config.use_quote_quantity,
            display_qty=display_qty,
            emulation_trigger=emulation_trigger,
        )

        if order_side == OrderSide.BUY:
            self.buy_order = order
        else:
            self.sell_order = order

        self.submit_order(
            order,
            client_id=self.client_id,
            params=self.config.order_params,
        )

    def submit_bracket_order(
        self,
        order_side: OrderSide,
        price: Price,
    ) -> None:
        """
        提交括号订单（入场限价单 + 止盈限价单 + 止损单）。
        """
        if not self.instrument:
            self.log.error("No instrument loaded")
            return

        if self.config.dry_run:
            self.log.warning(f"Dry run, skipping create {order_side} bracket order")
            return

        if order_side == OrderSide.BUY and not self.config.enable_limit_buys:
            self.log.warning("BUY orders not enabled, skipping")
            return
        elif order_side == OrderSide.SELL and not self.config.enable_limit_sells:
            self.log.warning("SELL orders not enabled, skipping")
            return

        if self.config.bracket_entry_order_type != OrderType.LIMIT:
            self.log.error("Only LIMIT entry bracket orders are currently supported")
            return

        # 入场单有效期
        entry_tif, entry_expire = self._resolve_time_in_force(
            self.config.limit_time_in_force,
        )
        # 止损单有效期
        sl_tif = self.config.stop_time_in_force or TimeInForce.GTC
        if sl_tif == TimeInForce.GTD:
            self.log.error("GTD time in force not supported for bracket stop-loss legs")
            return

        # 模拟触发类型
        emulation_trigger = (
            TriggerType[self.config.emulation_trigger]
            if isinstance(self.config.emulation_trigger, str)
            else (self.config.emulation_trigger or TriggerType.NO_TRIGGER)
        )

        # 止损触发类型
        trigger_type = (
            TriggerType[self.config.stop_trigger_type]
            if isinstance(self.config.stop_trigger_type, str)
            else (self.config.stop_trigger_type or TriggerType.DEFAULT)
        )

        # 计算止盈和止损的偏移价格
        target_offset = (
            self.instrument.price_increment * self.config.bracket_offset_ticks
        )
        stop_offset = self.instrument.price_increment * self.config.bracket_offset_ticks
        entry_value = Decimal(str(price))

        if order_side == OrderSide.BUY:
            tp_price = self.instrument.make_price(entry_value + target_offset)
            sl_trigger_price = self.instrument.make_price(entry_value - stop_offset)
        else:
            tp_price = self.instrument.make_price(entry_value - target_offset)
            sl_trigger_price = self.instrument.make_price(entry_value + stop_offset)

        # 创建订单列表（入场+止盈+止损）
        order_list = self.order_factory.bracket(
            instrument_id=self.config.instrument_id,
            order_side=order_side,
            quantity=self.instrument.make_qty(self.config.order_qty),
            quote_quantity=self.config.use_quote_quantity,
            emulation_trigger=emulation_trigger,
            entry_order_type=self.config.bracket_entry_order_type,
            entry_price=price,
            time_in_force=entry_tif,
            expire_time=entry_expire,
            entry_post_only=self.config.use_post_only,
            tp_price=tp_price,
            tp_time_in_force=entry_tif,
            tp_post_only=self.config.use_post_only,
            sl_trigger_price=sl_trigger_price,
            sl_trigger_type=trigger_type,
            sl_time_in_force=sl_tif,
        )

        entry_order = order_list.first
        if order_side == OrderSide.BUY:
            self.buy_order = entry_order
            self.buy_stop_order = None  # 止损单由括号订单管理，不再单独维护
        else:
            self.sell_order = entry_order
            self.sell_stop_order = None

        self.submit_order_list(
            order_list,
            client_id=self.client_id,
            params=self.config.order_params,
        )

    def submit_stop_order(
        self,
        order_side: OrderSide,
        trigger_price: Price,
        limit_price: Price | None = None,
    ) -> None:
        """
        提交止损单（根据配置的止损单类型）。
        """
        if not self.instrument:
            self.log.error("No instrument loaded")
            return

        if self.config.dry_run:
            self.log.warning(f"Dry run, skipping create {order_side} stop order")
            return

        if order_side == OrderSide.BUY and not self.config.enable_stop_buys:
            self.log.warning("BUY stop orders not enabled, skipping")
            return
        elif order_side == OrderSide.SELL and not self.config.enable_stop_sells:
            self.log.warning("SELL stop orders not enabled, skipping")
            return

        # 有效期
        time_in_force, expire_time = self._resolve_time_in_force(
            self.config.stop_time_in_force,
        )

        # 触发类型
        trigger_type = (
            TriggerType[self.config.stop_trigger_type]
            if isinstance(self.config.stop_trigger_type, str)
            else (self.config.stop_trigger_type or TriggerType.DEFAULT)
        )
        emulation_trigger = (
            TriggerType[self.config.emulation_trigger]
            if isinstance(self.config.emulation_trigger, str)
            else (self.config.emulation_trigger or TriggerType.NO_TRIGGER)
        )

        # 显示数量（用于冰山订单）
        display_qty = (
            self.instrument.make_qty(self.config.order_display_qty)
            if self.config.order_display_qty is not None
            else None
        )

        order = self._create_stop_order(
            order_side=order_side,
            trigger_price=trigger_price,
            limit_price=limit_price,
            trigger_type=trigger_type,
            time_in_force=time_in_force,
            expire_time=expire_time,
            display_qty=display_qty,
            emulation_trigger=emulation_trigger,
        )
        if order is None:
            return

        if order_side == OrderSide.BUY:
            self.buy_stop_order = order
        else:
            self.sell_stop_order = order

        self.submit_order(
            order,
            client_id=self.client_id,
            params=self.config.order_params,
        )

    def _create_stop_order(
        self,
        order_side: OrderSide,
        trigger_price: Price,
        limit_price: Price | None,
        trigger_type: TriggerType,
        time_in_force: TimeInForce,
        expire_time: pd.Timestamp | None,
        display_qty: Quantity | None,
        emulation_trigger: TriggerType,
    ) -> Order | None:
        """
        根据配置的止损单类型创建相应的订单对象。
        """
        assert self.instrument is not None

        if self.config.stop_order_type == OrderType.STOP_MARKET:
            return self.order_factory.stop_market(
                instrument_id=self.config.instrument_id,
                order_side=order_side,
                quantity=self.instrument.make_qty(self.config.order_qty),
                trigger_price=trigger_price,
                trigger_type=trigger_type,
                time_in_force=time_in_force,
                expire_time=expire_time,
                quote_quantity=self.config.use_quote_quantity,
                emulation_trigger=emulation_trigger,
            )
        elif self.config.stop_order_type == OrderType.STOP_LIMIT:
            if limit_price is None:
                self.log.error("STOP_LIMIT order requires limit_price")
                return None
            return self.order_factory.stop_limit(
                instrument_id=self.config.instrument_id,
                order_side=order_side,
                quantity=self.instrument.make_qty(self.config.order_qty),
                price=limit_price,
                trigger_price=trigger_price,
                trigger_type=trigger_type,
                time_in_force=time_in_force,
                expire_time=expire_time,
                post_only=False,
                quote_quantity=self.config.use_quote_quantity,
                display_qty=display_qty,
                emulation_trigger=emulation_trigger,
            )
        elif self.config.stop_order_type == OrderType.MARKET_IF_TOUCHED:
            return self.order_factory.market_if_touched(
                instrument_id=self.config.instrument_id,
                order_side=order_side,
                quantity=self.instrument.make_qty(self.config.order_qty),
                trigger_price=trigger_price,
                trigger_type=trigger_type,
                time_in_force=time_in_force,
                expire_time=expire_time,
                quote_quantity=self.config.use_quote_quantity,
                emulation_trigger=emulation_trigger,
            )
        elif self.config.stop_order_type == OrderType.LIMIT_IF_TOUCHED:
            if limit_price is None:
                self.log.error("LIMIT_IF_TOUCHED order requires limit_price")
                return None
            return self.order_factory.limit_if_touched(
                instrument_id=self.config.instrument_id,
                order_side=order_side,
                quantity=self.instrument.make_qty(self.config.order_qty),
                price=limit_price,
                trigger_price=trigger_price,
                trigger_type=trigger_type,
                time_in_force=time_in_force,
                expire_time=expire_time,
                post_only=False,
                quote_quantity=self.config.use_quote_quantity,
                display_qty=display_qty,
                emulation_trigger=emulation_trigger,
            )
        elif self.config.stop_order_type == OrderType.TRAILING_STOP_MARKET:
            if self.config.trailing_offset is None:
                self.log.error(
                    "TRAILING_STOP_MARKET order requires trailing_offset config"
                )
                return None
            return self.order_factory.trailing_stop_market(
                instrument_id=self.config.instrument_id,
                order_side=order_side,
                quantity=self.instrument.make_qty(self.config.order_qty),
                trailing_offset=self.config.trailing_offset,
                trailing_offset_type=self.config.trailing_offset_type,
                activation_price=trigger_price,
                trigger_type=trigger_type,
                time_in_force=time_in_force,
                expire_time=expire_time,
                quote_quantity=self.config.use_quote_quantity,
                emulation_trigger=emulation_trigger,
            )
        else:
            self.log.error(f"Unknown stop order type: {self.config.stop_order_type}")
            return None

    def maintain_stop_buy_orders(
        self,
        instrument: Instrument,
        best_bid: Price,
        best_ask: Price,
    ) -> None:
        """
        维护止损买单：根据当前市场计算触发价格，必要时创建或调整订单。
        """
        stop_offset = instrument.price_increment * self.config.stop_offset_ticks

        # 根据止损单类型决定触发价格的方向
        if self.config.stop_order_type in (
            OrderType.LIMIT_IF_TOUCHED,
            OrderType.MARKET_IF_TOUCHED,
        ):
            # IF_TOUCHED买单：触发价格低于当前买价（逢低买入）
            trigger_price = instrument.make_price(best_bid - stop_offset)
        else:
            # 标准止损买单：触发价格高于当前卖价（空头止损）
            trigger_price = instrument.make_price(best_ask + stop_offset)

        limit_price = None
        if self.config.stop_order_type in (
            OrderType.STOP_LIMIT,
            OrderType.LIMIT_IF_TOUCHED,
        ):
            if self.config.stop_limit_offset_ticks:
                limit_offset = (
                    instrument.price_increment * self.config.stop_limit_offset_ticks
                )
                if self.config.stop_order_type == OrderType.LIMIT_IF_TOUCHED:
                    # IF_TOUCHED买单的限价应低于触发价格（更好的价格）
                    limit_price = instrument.make_price(trigger_price - limit_offset)
                else:
                    # STOP_LIMIT买单的限价应高于触发价格（可接受更差的价格）
                    limit_price = instrument.make_price(trigger_price + limit_offset)
            else:
                # 默认使用触发价格作为限价
                limit_price = trigger_price

        if not self.buy_stop_order or not self.is_order_active(self.buy_stop_order):
            self.submit_stop_order(OrderSide.BUY, trigger_price, limit_price)
        elif (
            self.buy_stop_order
            and self.buy_stop_order.venue_order_id
            and not self.buy_stop_order.is_pending_update
            and not self.buy_stop_order.is_pending_cancel
        ):
            # 如果已有活跃订单，检查触发价格是否变化，必要时调整
            current_trigger = self.get_order_trigger_price(self.buy_stop_order)
            if current_trigger and current_trigger != trigger_price:
                if self.config.modify_stop_orders_to_maintain_offset:
                    self.modify_stop_order(
                        self.buy_stop_order, trigger_price, limit_price
                    )
                elif self.config.cancel_replace_stop_orders_to_maintain_offset:
                    self.cancel_order(self.buy_stop_order)
                    self.submit_stop_order(OrderSide.BUY, trigger_price, limit_price)

    def maintain_stop_sell_orders(
        self,
        instrument: Instrument,
        best_bid: Price,
        best_ask: Price,
    ) -> None:
        """
        维护止损卖单。
        """
        stop_offset = instrument.price_increment * self.config.stop_offset_ticks

        if self.config.stop_order_type in (
            OrderType.LIMIT_IF_TOUCHED,
            OrderType.MARKET_IF_TOUCHED,
        ):
            # IF_TOUCHED卖单：触发价格高于当前卖价（逢高卖出）
            trigger_price = instrument.make_price(best_ask + stop_offset)
        else:
            # 标准止损卖单：触发价格低于当前买价（多头止损）
            trigger_price = instrument.make_price(best_bid - stop_offset)

        limit_price = None
        if self.config.stop_order_type in (
            OrderType.STOP_LIMIT,
            OrderType.LIMIT_IF_TOUCHED,
        ):
            if self.config.stop_limit_offset_ticks:
                limit_offset = (
                    instrument.price_increment * self.config.stop_limit_offset_ticks
                )
                if self.config.stop_order_type == OrderType.LIMIT_IF_TOUCHED:
                    # IF_TOUCHED卖单的限价应高于触发价格（更好的价格）
                    limit_price = instrument.make_price(trigger_price + limit_offset)
                else:
                    # STOP_LIMIT卖单的限价应低于触发价格（可接受更差的价格）
                    limit_price = instrument.make_price(trigger_price - limit_offset)
            else:
                limit_price = trigger_price

        if not self.sell_stop_order or not self.is_order_active(self.sell_stop_order):
            self.submit_stop_order(OrderSide.SELL, trigger_price, limit_price)
        elif (
            self.sell_stop_order
            and self.sell_stop_order.venue_order_id
            and not self.sell_stop_order.is_pending_update
            and not self.sell_stop_order.is_pending_cancel
        ):
            current_trigger = self.get_order_trigger_price(self.sell_stop_order)
            if current_trigger and current_trigger != trigger_price:
                if self.config.modify_stop_orders_to_maintain_offset:
                    self.modify_stop_order(
                        self.sell_stop_order, trigger_price, limit_price
                    )
                elif self.config.cancel_replace_stop_orders_to_maintain_offset:
                    self.cancel_order(self.sell_stop_order)
                    self.submit_stop_order(OrderSide.SELL, trigger_price, limit_price)

    def get_order_trigger_price(self, order: Order) -> Price | None:
        """获取订单的触发价格（如果支持）"""
        if isinstance(
            order,
            StopMarketOrder
            | StopLimitOrder
            | MarketIfTouchedOrder
            | LimitIfTouchedOrder
            | TrailingStopMarketOrder,
        ):
            return order.trigger_price
        return None

    def modify_stop_order(
        self,
        order: Order,
        trigger_price: Price,
        limit_price: Price | None = None,
    ) -> None:
        """
        修改止损订单的触发价格和/或限价。
        """
        if isinstance(
            order, StopMarketOrder | MarketIfTouchedOrder | TrailingStopMarketOrder
        ):
            self.modify_order(order, trigger_price=trigger_price)
        elif isinstance(order, StopLimitOrder | LimitIfTouchedOrder):
            if limit_price is not None:
                self.modify_order(order, price=limit_price, trigger_price=trigger_price)
            else:
                self.modify_order(order, trigger_price=trigger_price)
        else:
            self.log.warning(f"Cannot modify order of type {type(order).__name__}")

    def on_stop(self) -> None:  # noqa: C901 (too complex)
        """
        策略停止时执行的操作：撤销订单、平仓、取消订阅。
        """
        if self.config.dry_run:
            self.log.warning(
                "Dry run mode, skipping cancel all orders and close all positions"
            )
            return

        # 撤销所有订单
        if self.config.cancel_orders_on_stop:
            if self.config.use_individual_cancels_on_stop:
                for order in self.cache.orders_open(
                    instrument_id=self.config.instrument_id,
                    strategy_id=self.id,
                ):
                    self.cancel_order(order)
            elif self.config.use_batch_cancel_on_stop:
                open_orders = self.cache.orders_open(
                    instrument_id=self.config.instrument_id,
                    strategy_id=self.id,
                )
                if open_orders:
                    self.cancel_orders(open_orders, client_id=self.client_id)
            else:
                self.cancel_all_orders(
                    self.config.instrument_id, client_id=self.client_id
                )

        # 平仓
        if self.config.close_positions_on_stop:
            self.close_all_positions(
                instrument_id=self.config.instrument_id,
                client_id=self.client_id,
                time_in_force=self.config.close_positions_time_in_force
                or TimeInForce.GTC,
                reduce_only=self.config.reduce_only_on_stop,
            )

        # 取消订阅数据（如果支持）
        if self.config.can_unsubscribe:
            if self.config.subscribe_quotes:
                self.unsubscribe_quote_ticks(
                    self.config.instrument_id, client_id=self.client_id
                )

            if self.config.subscribe_trades:
                self.unsubscribe_trade_ticks(
                    self.config.instrument_id, client_id=self.client_id
                )

            if self.config.subscribe_book:
                self.unsubscribe_order_book_at_interval(
                    self.config.instrument_id,
                    client_id=self.client_id,
                )
