#!/usr/bin/env python3
"""
用户体验评分器（10分）

评分维度：
- 易用性（5分）：快速开始指南
- 文档可读性（5分）：结构组织、平均行长度
"""

from typing import Dict
from . import utils


class UXScorer:
    """用户体验评分器"""

    def __init__(self, config: Dict):
        """
        初始化评分器

        Args:
            config: 配置字典
        """
        self.config = config
        self.weights = config['weights']['user_experience']
        self.analysis = config['analysis']
        self.keywords = config['keywords']

    def score(self, content: str) -> Dict:
        """
        计算用户体验评分

        Args:
            content: SKILL.md 内容

        Returns:
            评分结果字典
        """
        ease_score = self._score_ease_of_use(content)
        readability_score = self._score_readability(content)

        total = ease_score + readability_score

        return {
            'total': total,
            'max': self.weights['total'],
            'ease_of_use': ease_score,
            'readability': readability_score,
            'details': {
                'has_quick_start': utils.check_keywords(content, self.keywords['quick_start']),
                'use_cases_count': len(utils.extract_use_cases(content)),
                'sections_count': utils.count_sections(content),
                'avg_line_length': utils.calculate_avg_line_length(content),
            }
        }

    def _score_ease_of_use(self, content: str) -> int:
        """
        评分：易用性（5分）

        检查项：
        - Quick Start 章节（3分）
        - 使用场景列表（2分）

        Args:
            content: SKILL.md 内容

        Returns:
            易用性得分（0-5）
        """
        score = 0

        # Quick Start 章节（3分）
        quick_start_keywords = self.keywords['quick_start']

        if utils.has_section(content, 'Quick Start') or \
           utils.has_section(content, 'Getting Started'):
            score += 3
        elif utils.check_keywords(content, quick_start_keywords):
            score += 2

        # 使用场景列表（2分）
        use_cases = utils.extract_use_cases(content)

        if len(use_cases) > 0:
            score += 2

        return min(score, self.weights['ease_of_use'])

    def _score_readability(self, content: str) -> int:
        """
        评分：文档可读性（5分）

        检查项：
        - 平均行长度（3分，理想范围 40-100 字符）
        - 章节结构（2分）

        Args:
            content: SKILL.md 内容

        Returns:
            文档可读性得分（0-5）
        """
        score = 0

        # 平均行长度（3分）
        avg_line_length = utils.calculate_avg_line_length(content)
        ideal_min = self.analysis['ideal_avg_line_length_min']
        ideal_max = self.analysis['ideal_avg_line_length_max']

        if ideal_min <= avg_line_length <= ideal_max:
            # 理想范围 - 3分
            score += 3
        elif avg_line_length > 0:
            # 非理想但有内容 - 1分
            score += 1

        # 章节结构（2分）
        sections_count = utils.count_sections(content)
        min_sections = self.analysis['min_sections_for_full_score']

        if sections_count >= min_sections:
            score += 2
        elif sections_count >= min_sections // 2:
            score += 1

        return min(score, self.weights['readability'])
