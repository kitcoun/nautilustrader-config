"""
环境变量配置加载器
支持以 NAUTILUS__ 开头的环境变量，优先级高于配置文件
"""
import os
import re
import json
from typing import Dict, Any, Optional, List

class ConfigLoader:
    """环境变量配置加载器"""
    
    def __init__(self, prefix: str = "NAUTILUS__"):
        self.prefix = prefix
        self.env_vars = self._collect_env_vars()
    
    def _collect_env_vars(self) -> Dict[str, Any]:
        """收集所有以指定前缀开头的环境变量"""
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                # 移除前缀并转换为小写
                config_key = key[len(self.prefix):].lower()
                env_vars[config_key] = self._parse_value(value)
        return env_vars
    
    def _parse_value(self, value: str) -> Any:
        """解析环境变量值"""
        # 尝试解析为 JSON
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            pass
        
        # 尝试解析为布尔值
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # 尝试解析为数字
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # 默认为字符串
        return value
    
    def _convert_to_nested_dict(self, flat_dict: Dict[str, Any]) -> Dict[str, Any]:
        """将扁平的环境变量转换为嵌套字典结构"""
        nested_dict = {}
        
        for key, value in flat_dict.items():
            # 将下划线转换为嵌套结构
            keys = key.split('__')
            current_level = nested_dict
            
            for i, k in enumerate(keys):
                if i == len(keys) - 1:
                    # 最后一个键，设置值
                    current_level[k] = value
                else:
                    # 中间键，创建嵌套字典
                    if k not in current_level:
                        current_level[k] = {}
                    current_level = current_level[k]
        
        return nested_dict
    
    def get_config_dict(self) -> Dict[str, Any]:
        """获取环境变量配置字典"""
        return self._convert_to_nested_dict(self.env_vars)
    
    def has_config(self) -> bool:
        """检查是否存在环境变量配置"""
        return len(self.env_vars) > 0

# 示例用法
if __name__ == "__main__":
    loader = ConfigLoader()
    config = loader.get_config_dict()
    print("Environment config:", json.dumps(config, indent=2))