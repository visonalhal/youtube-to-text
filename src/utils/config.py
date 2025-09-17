"""
配置文件管理模块
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class Config:
    """配置管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logger.info(f"配置文件加载成功: {self.config_path}")
                return config
            except Exception as e:
                logger.error(f"配置文件加载失败: {str(e)}")
                return self._get_default_config()
        else:
            logger.info("配置文件不存在，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'download': {
                'output_dir': 'output/videos',
                'format': 'best[height<=720]',
                'audio_only': False,
                'audio_format': 'mp3',
                'audio_quality': '192k'
            },
            'converter': {
                'output_dir': 'output/audios',
                'audio_format': 'mp3',
                'quality': '192k',
                'channels': 1
            },
            'transcriber': {
                'output_dir': 'output/texts',
                'model_size': 'base',
                'language': None,
                'task': 'transcribe'
            },
            'logging': {
                'level': 'INFO',
                'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}',
                'file': 'logs/app.log'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键，支持点号分隔 (如 'download.output_dir')
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def save(self):
        """保存配置到文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
            logger.info(f"配置已保存: {self.config_path}")
        except Exception as e:
            logger.error(f"配置保存失败: {str(e)}")
    
    def update(self, updates: Dict[str, Any]):
        """
        批量更新配置
        
        Args:
            updates: 更新的配置字典
        """
        def deep_update(base_dict, update_dict):
            for key, value in update_dict.items():
                if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
                    deep_update(base_dict[key], value)
                else:
                    base_dict[key] = value
        
        deep_update(self.config, updates)
        logger.info("配置已更新")


def create_default_config():
    """创建默认配置文件"""
    config = Config()
    config.save()
    logger.info("默认配置文件已创建")


if __name__ == "__main__":
    # 创建默认配置文件
    create_default_config()
