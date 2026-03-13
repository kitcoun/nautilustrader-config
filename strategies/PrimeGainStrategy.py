from nautilus_trader.model.data.bar import Bar
from intermediary.strategies.IStrategy import IStrategy
from indicator import SuperTrend


class PrimeGainStrategy(IStrategy):
    def populate_indicators(self, bar: Bar) -> None:
        """
        虚方法：生成和注册指标。
        子类需要实现此方法来创建具体的指标实例。
        """
        pass

    def populate_entry_trend(self, bar: Bar, metadata: dict) -> None:
        "入场信号"
        pass

    def populate_exit_trend(self, bar: Bar, metadata: dict) -> None:
        "出场信号"
        pass
