"""
混合配置管理器
整合环境变量和文件配置，环境变量优先级更高
"""

from pathlib import Path
from typing import Dict, Any, Optional

from .ConfigLoader import ConfigLoader
from .LoadConfig import LoadConfig


class HybridConfiguration:
    """混合配置管理器"""

    def __init__(
        self, config_file_path: Optional[str] = None, env_prefix: str = "NAUTILUS__"
    ):
        self.config_file_path = config_file_path
        self.env_prefix = env_prefix
        self._config = None

        # 初始化加载器
        self.env_loader = ConfigLoader(prefix=env_prefix)
        self.file_config = None

        if config_file_path and Path(config_file_path).exists():
            self.file_config = LoadConfig.load_config(config_file_path)

    def _merge_configs(
        self, file_config: dict, env_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """合并文件配置和环境变量配置"""

        def deep_merge(
            base: Dict[str, Any], override: Dict[str, Any]
        ) -> Dict[str, Any]:
            """深度合并两个字典"""
            result = base.copy()

            for key, value in override.items():
                if (
                    key in result
                    and isinstance(result[key], dict)
                    and isinstance(value, dict)
                ):
                    # 递归合并嵌套字典
                    result[key] = deep_merge(result[key], value)
                else:
                    # 覆盖或添加新键
                    result[key] = value

            return result

        return deep_merge(file_config, env_config)

    def load(self) -> Dict[str, Any]:
        """加载配置"""
        env_config = self.env_loader.get_config_dict()

        if self.file_config:
            # 合并环境变量和文件配置
            merged_config = self._merge_configs(self.file_config, env_config)
            self._config = merged_config
        else:
            # 只有环境变量配置
            self._config = env_config

        return self._config

    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        if self._config is None:
            self.load()

        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value


if __name__ == "__main__":
    # 测试配置加载
    pass
