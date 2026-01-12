#!/usr/bin/env python3
"""
维护性评分器（10分）

评分维度：
- 更新频率（3分）：基于 metadata.json 的 updatedAt 字段
- 社区活跃度（5分）：基于 stars 数量
- 兼容性（2分）：版本说明、依赖管理
"""

from typing import Dict, Optional
from datetime import datetime
from . import utils


class MaintenanceScorer:
    """维护性评分器"""

    def __init__(self, config: Dict):
        """
        初始化评分器

        Args:
            config: 配置字典
        """
        self.config = config
        self.weights = config['weights']['maintenance']
        self.analysis = config['analysis']
        self.stars_thresholds = config['stars_thresholds']

    def score(self, metadata: Optional[Dict], content: str) -> Dict:
        """
        计算维护性评分

        Args:
            metadata: metadata.json 数据（可能为 None）
            content: SKILL.md 内容

        Returns:
            评分结果字典
        """
        update_score = self._score_update_frequency(metadata)
        community_score = self._score_community_activity(metadata)
        compatibility_score = self._score_compatibility(content)

        total = update_score + community_score + compatibility_score

        return {
            'total': total,
            'max': self.weights['total'],
            'update_frequency': update_score,
            'community_activity': community_score,
            'compatibility': compatibility_score,
            'details': {
                'has_metadata': metadata is not None,
                'days_since_update': self._calculate_days_since_update(metadata) if metadata else None,
                'stars': metadata.get('stars', 0) if metadata else 0,
                'has_version_info': 'version' in content.lower(),
            }
        }

    def _score_update_frequency(self, metadata: Optional[Dict]) -> int:
        """
        评分：更新频率（3分）

        检查项：
        - 距离上次更新的天数

        Args:
            metadata: metadata.json 数据

        Returns:
            更新频率得分（0-3）
        """
        if not metadata or 'updatedAt' not in metadata:
            return 0

        days_since_update = self._calculate_days_since_update(metadata)

        if days_since_update < self.analysis['recent_update_days']:
            # 最近90天内更新 - 3分
            return 3
        elif days_since_update < self.analysis['active_update_days']:
            # 90-180天内更新 - 2分
            return 2
        elif days_since_update < 365:
            # 180-365天内更新 - 1分
            return 1
        else:
            # 超过1年未更新 - 0分
            return 0

    def _score_community_activity(self, metadata: Optional[Dict]) -> int:
        """
        评分：社区活跃度（5分）

        检查项：
        - GitHub stars 数量

        Args:
            metadata: metadata.json 数据

        Returns:
            社区活跃度得分（0-5）
        """
        if not metadata or 'stars' not in metadata:
            return 0

        stars = metadata['stars']

        if stars >= self.stars_thresholds['excellent']:
            # 10,000+ stars - 5分
            return 5
        elif stars >= self.stars_thresholds['good']:
            # 1,000+ stars - 4分
            return 4
        elif stars >= self.stars_thresholds['fair']:
            # 100+ stars - 3分
            return 3
        elif stars >= 10:
            # 10+ stars - 2分
            return 2
        elif stars >= 1:
            # 1+ stars - 1分
            return 1
        else:
            return 0

    def _score_compatibility(self, content: str) -> int:
        """
        评分：兼容性（2分）

        检查项：
        - 版本说明（1分）
        - 依赖管理（1分）

        Args:
            content: SKILL.md 内容

        Returns:
            兼容性得分（0-2）
        """
        score = 0

        # 版本说明（1分）
        version_keywords = ['version', 'v1', 'v2', '版本']
        if utils.check_keywords(content, version_keywords):
            score += 1

        # 依赖管理（1分）
        dependency_keywords = ['dependency', 'requirement', 'install', 'npm', 'pip', '依赖']
        if utils.check_keywords(content, dependency_keywords):
            score += 1

        return min(score, self.weights['compatibility'])

    def _calculate_days_since_update(self, metadata: Optional[Dict]) -> Optional[int]:
        """
        计算距离上次更新的天数

        Args:
            metadata: metadata.json 数据

        Returns:
            天数，如果无法计算则返回 None
        """
        if not metadata or 'updatedAt' not in metadata:
            return None

        try:
            updated_timestamp = metadata['updatedAt']
            # 自动处理毫秒级时间戳
            # 阈值 1e11 对应 1973-03-03（秒级）或 1970-01-02（毫秒级）
            # 如果时间戳大于此值，认为是毫秒级时间戳，需转换为秒
            if updated_timestamp > 1e11:
                updated_timestamp = updated_timestamp / 1000
            updated_date = datetime.fromtimestamp(updated_timestamp)
            now = datetime.now()
            delta = now - updated_date
            return delta.days
        except (ValueError, TypeError, OSError):
            return None
