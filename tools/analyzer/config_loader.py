"""
配置加载器 - 用于加载评分系统的配置文件

此模块提供统一的配置加载接口，支持：
- YAML 配置文件加载
- 默认值回退机制
- 向后兼容（配置缺失时使用内置默认值）
- 配置验证

Created: 2026-01-13
Author: Ordinary Claude Skills Team
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ScoringConfig:
    """
    评分配置管理器

    用法示例：
        config = ScoringConfig()
        params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
        # 返回: {'max_value': 5, 'max_score': 5}
    """

    # 内置默认配置（向后兼容）
    DEFAULT_CONFIG = {
        'content_quality': {
            'clarity': {
                'use_cases': {'max_value': 5, 'max_score': 5}
            },
            'technical_depth': {
                'code_blocks': {'max_value': 8, 'max_score': 7},
                'best_practices': {'max_value': 5, 'max_score': 4}
            },
            'documentation': {
                'sections': {'max_value': 10, 'max_score': 6},
                'examples': {'max_value': 5, 'max_score': 4}
            }
        },
        'technical_implementation': {
            'code_quality': {
                'code_block_count': {'max_value': 5, 'max_score': 5}
            }
        },
        'general': {
            'default_max_value': 5,
            'default_max_score': 5,
            'backward_compatible': True,
            'debug_mode': False
        }
    }

    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        """
        初始化配置加载器

        Args:
            config_path: 配置文件路径（可选）
                        如果不提供，使用默认路径 tools/config/scoring.yml
        """
        self.config_path = self._resolve_config_path(config_path)
        self.config = self._load_config()
        self.debug_mode = self.config.get('general', {}).get('debug_mode', False)

        if self.debug_mode:
            logger.info(f"配置已加载自: {self.config_path}")

    def _resolve_config_path(self, config_path: Optional[Union[str, Path]]) -> Path:
        """
        解析配置文件路径

        Args:
            config_path: 用户提供的路径（可选）

        Returns:
            解析后的 Path 对象
        """
        if config_path:
            return Path(config_path)

        # 默认路径：tools/config/scoring.yml
        # 从当前文件位置推断项目根目录
        current_file = Path(__file__)  # tools/analyzer/config_loader.py
        analyzer_dir = current_file.parent  # tools/analyzer/
        tools_dir = analyzer_dir.parent     # tools/
        config_dir = tools_dir / 'config'   # tools/config/

        return config_dir / 'scoring.yml'

    def _load_config(self) -> Dict[str, Any]:
        """
        加载配置文件

        Returns:
            配置字典

        Raises:
            FileNotFoundError: 配置文件不存在且未启用向后兼容模式
        """
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}")
            logger.warning("使用内置默认配置（向后兼容模式）")
            return self.DEFAULT_CONFIG.copy()

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                loaded_config = yaml.safe_load(f)

            if not loaded_config:
                logger.warning("配置文件为空，使用内置默认配置")
                return self.DEFAULT_CONFIG.copy()

            # 合并默认配置和加载的配置（加载的配置优先）
            merged_config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)

            logger.info(f"成功加载配置文件: {self.config_path}")
            return merged_config

        except yaml.YAMLError as e:
            logger.error(f"配置文件解析失败: {e}")
            logger.warning("使用内置默认配置（向后兼容模式）")
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"加载配置文件时出错: {e}")
            logger.warning("使用内置默认配置（向后兼容模式）")
            return self.DEFAULT_CONFIG.copy()

    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """
        递归合并两个配置字典

        Args:
            default: 默认配置
            loaded: 加载的配置

        Returns:
            合并后的配置（loaded 中的值会覆盖 default）
        """
        result = default.copy()

        for key, value in loaded.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # 递归合并嵌套字典
                result[key] = self._merge_configs(result[key], value)
            else:
                # 直接覆盖
                result[key] = value

        return result

    def get_smooth_params(self, *path: str) -> Dict[str, int]:
        """
        获取 smooth_score 函数的参数

        Args:
            *path: 配置路径，例如：
                  ('content_quality', 'clarity', 'use_cases')
                  ('technical_implementation', 'code_quality', 'code_block_count')

        Returns:
            包含 max_value 和 max_score 的字典

        Examples:
            >>> config = ScoringConfig()
            >>> config.get_smooth_params('content_quality', 'clarity', 'use_cases')
            {'max_value': 5, 'max_score': 5}

            >>> config.get_smooth_params('technical_implementation', 'code_quality', 'code_block_count')
            {'max_value': 5, 'max_score': 5}
        """
        # 遍历路径获取配置
        current = self.config
        for key in path:
            if not isinstance(current, dict) or key not in current:
                # 路径不存在，返回默认值
                return self._get_default_params()
            current = current[key]

        # 验证返回值包含必需的字段
        if not isinstance(current, dict):
            logger.warning(f"配置路径 {'.'.join(path)} 不是字典，使用默认值")
            return self._get_default_params()

        if 'max_value' not in current or 'max_score' not in current:
            logger.warning(f"配置路径 {'.'.join(path)} 缺少必需字段，使用默认值")
            return self._get_default_params()

        result = {
            'max_value': current['max_value'],
            'max_score': current['max_score']
        }

        if self.debug_mode:
            logger.debug(f"获取配置 {'.'.join(path)}: {result}")

        return result

    def _get_default_params(self) -> Dict[str, int]:
        """
        获取默认的 smooth_score 参数

        Returns:
            默认参数字典
        """
        general = self.config.get('general', {})
        return {
            'max_value': general.get('default_max_value', 5),
            'max_score': general.get('default_max_score', 5)
        }

    def get(self, *path: str, default: Any = None) -> Any:
        """
        通用配置获取方法

        Args:
            *path: 配置路径
            default: 默认值（如果路径不存在）

        Returns:
            配置值

        Examples:
            >>> config.get('general', 'debug_mode')
            False

            >>> config.get('metadata', 'version')
            '1.0.0'
        """
        current = self.config
        for key in path:
            if not isinstance(current, dict) or key not in current:
                return default
            current = current[key]
        return current

    def reload(self):
        """
        重新加载配置文件

        用于配置文件被修改后动态刷新
        """
        self.config = self._load_config()
        logger.info("配置已重新加载")


# 全局单例（避免重复加载配置文件）
_global_config: Optional[ScoringConfig] = None


def get_config(reload: bool = False) -> ScoringConfig:
    """
    获取全局配置单例

    Args:
        reload: 是否强制重新加载配置文件

    Returns:
        ScoringConfig 实例

    Examples:
        >>> from analyzer.config_loader import get_config
        >>> config = get_config()
        >>> params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
    """
    global _global_config

    if _global_config is None or reload:
        _global_config = ScoringConfig()

    return _global_config
