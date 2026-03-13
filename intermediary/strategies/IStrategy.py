from abc import ABC, abstractmethod
from nautilus_trader.model.data.bar import Bar


class IStrategy(ABC):
    """
    指标策略抽象基类，定义指标生成和处理的抽象方法。
    这个类应该由具体的策略实现类继承，然后在BaseStrategy中调用。
    """

    @abstractmethod
    def populate_indicators(self, bar: Bar) -> None:
        """
        虚方法：生成和注册指标。
        子类需要实现此方法来创建具体的指标实例。
        """
        pass

    @abstractmethod
    def populate_entry_trend(self, bar: Bar, metadata: dict) -> None:
        "入场信号"
        
        # 本方法最后返回需要与这个类似,多个条件的组合，入场方向，信号有效性，信号标签名称
        # 并且可以返回多个组合
        # dataframe.loc[
        #     (dataframe["supertrend_trend_change_1h"] == -1)
        #     & (dataframe["supertrend_trend_1h"].shift(1) != -1),
        #     ["enter_long", "enter_tag"],
        # ] = (1, "enter_bb_width8")
        pass

    @abstractmethod
    def populate_exit_trend(self, bar: Bar, metadata: dict) -> None:
        "出场信号"        
        # 本方法最后返回需要与这个类似,多个条件的组合，出场方向，信号有效性，信号标签名称
        # 并且可以返回多个组合
        # dataframe.loc[
        #     (dataframe["supertrend_trend_change_1h"] == -1)
        #     & (dataframe["supertrend_trend_1h"].shift(1) != -1),
        #     ["exit_long", "exit_tag"],
        # ] = (1, "exit_st_1h")
        pass
