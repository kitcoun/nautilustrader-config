"""
Hybrid Trader 配置加载器
此模块加载并验证 Freqtrade 风格的配置文件
"""

import json
from pathlib import Path


class LoadConfig:

    def load_config(config_path: str) -> dict:
        """
        从 JSON 文件加载配置

        参数:
            config_path: JSON 配置文件路径

        返回:
            Config 对象
        """
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(path, "r") as f:
            config_dict = json.load(f)

        return config_dict


if __name__ == "__main__":
    # 测试配置加载器
    pass
