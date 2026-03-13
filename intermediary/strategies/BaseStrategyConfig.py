from typing import List
from nautilus_trader.config import StrategyConfig
from nautilus_trader.model.identifiers import InstrumentId
from nautilus_trader.model.data import BarType
from nautilus_trader.trading.strategy import Strategy
from nautilus_trader.model.enums import OrderSide
from nautilus_trader.common.config import PositiveInt
from nautilus_trader.model.enums import TimeInForce


class BaseStrategyConfig(StrategyConfig):
    """
    所有交易策略配置的基础模型。

    参数
    ----------
    strategy_id : StrategyId, optional
        策略的唯一ID。如果不为None，将作为策略ID。
    order_id_tag : str, optional
        策略的唯一订单ID标签。对于特定交易者ID的所有运行策略中必须唯一。
    use_uuid_client_order_ids : bool, default False
        是否应使用UUID4作为客户端订单ID的值。
    use_hyphens_in_client_order_ids : bool, default True
        是否在生成的客户端订单ID中使用连字符。
    oms_type : OmsType, optional
        策略的订单管理系统类型。这将决定`ExecutionEngine`如何处理仓位ID。
    external_order_claims : list[InstrumentId], optional
        外部订单声明的工具ID列表。匹配该工具ID的外部订单将被该策略关联（声明）。
    manage_contingent_orders : bool, default False
        是否应由策略自动管理OTO、OCO和OUO类型的**未成交**条件订单。
        任何处于本地活动状态的模拟订单将由`OrderEmulator`管理。
    manage_gtd_expiry : bool, default False
        是否应由策略管理所有订单的GTD（指定日期时间）到期。
        如果为True，则在启动时将确保未成交订单的GTD计时器重新激活。
    manage_stop : bool, default False
        当策略停止时是否自动执行市场退出。
        如果为True，调用stop()将首先取消所有订单并平掉所有仓位，
        然后策略才会转换到STOPPED状态。
    market_exit_interval_ms : int, default 100
        市场退出期间检查进行中的订单和未平仓仓位的间隔时间（毫秒）。
    market_exit_max_attempts : int, default 100
        市场退出期间等待订单和仓位关闭的最大尝试次数。默认100次尝试
        （在100毫秒间隔下相当于10秒）。
    market_exit_time_in_force : TimeInForce, default ``GTC``
        市场退出期间平仓市价单的时效类型。
    market_exit_reduce_only : bool, default True
        市场退出期间平仓市价单是否应为仅减仓。
    log_events : bool, default True
        策略是否应记录事件日志。如果为False，则仅记录警告及以上级别的事件。
    log_commands : bool, default True
        策略是否应记录命令日志。
    log_rejected_due_post_only_as_warning : bool, default True
        当订单因`due_post_only`（仅做市商）而被拒时，是否应作为警告记录。
    """

    # order_id_tag: str | None = None  # 订单ID标签，在交易者ID下必须唯一
    use_uuid_client_order_ids: bool = False  # 是否使用UUID4作为客户端订单ID
    use_hyphens_in_client_order_ids: bool = True  # 生成的客户端订单ID中是否使用连字符
    oms_type: str | None = None  # OMS类型，影响仓位ID处理
    external_order_claims: list[InstrumentId] | None = (
        None  # 外部订单声明列表，关联外部订单
    )
    manage_contingent_orders: bool = False  # 是否自动管理未成交条件订单（OTO/OCO/OUO）
    manage_gtd_expiry: bool = False  # 是否管理GTD订单的到期时间
    manage_stop: bool = False  # 停止时是否自动平仓退出
    market_exit_interval_ms: PositiveInt = 100  # 市场退出检查间隔（毫秒）
    market_exit_max_attempts: PositiveInt = 100  # 市场退出最大尝试次数
    market_exit_time_in_force: TimeInForce = TimeInForce.GTC  # 市场退出订单的时效类型
    market_exit_reduce_only: bool = True  # 市场退出订单是否仅减仓
    log_events: bool = True  # 是否记录事件日志
    log_commands: bool = True  # 是否记录命令日志
    log_rejected_due_post_only_as_warning: bool = (
        True  # 是否将因post-only被拒的订单记录为警告
    )

    # 自定义配置
    # 所有config.example.json配置参数都可以传递过来
    strategy_ids: List[strategy_config]  # 策略唯一ID，可选

# 需要这个代码，修改符合的名称
class strategy_config:
    strategy_ids: InstrumentId
    bar_types: BarType
