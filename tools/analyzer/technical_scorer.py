#!/usr/bin/env python3
"""
技术实现评分器（30分）

评分维度：
- 代码示例质量（15分）：代码正确性、安全性考虑、错误处理
- 模式设计（10分）：设计模式应用、架构合理性
- 错误处理（5分）：异常处理覆盖
"""

from typing import Dict, List
from . import utils


class TechnicalScorer:
    """技术实现评分器"""

    def __init__(self, config: Dict):
        """
        初始化评分器

        Args:
            config: 配置字典
        """
        self.config = config
        self.weights = config['weights']['technical_implementation']
        self.keywords = config['keywords']

    def score(self, content: str) -> Dict:
        """
        计算技术实现评分

        Args:
            content: SKILL.md 内容

        Returns:
            评分结果字典
        """
        code_quality_score = self._score_code_quality(content)
        pattern_score = self._score_pattern_design(content)
        error_handling_score = self._score_error_handling(content)

        total = code_quality_score + pattern_score + error_handling_score

        return {
            'total': total,
            'max': self.weights['total'],
            'code_quality': code_quality_score,
            'pattern_design': pattern_score,
            'error_handling': error_handling_score,
            'details': {
                'code_blocks_count': utils.count_code_blocks(content),
                'has_security_keywords': utils.check_keywords(content, self.keywords['security']),
                'design_patterns_found': self._detect_patterns(content),
                'has_error_handling': utils.check_keywords(content, self.keywords['error_handling']),
            }
        }

    def _score_code_quality(self, content: str) -> int:
        """
        评分：代码示例质量（15分）

        检查项：
        - 代码块数量和长度（8分）
        - 安全性关键词（4分）
        - 错误处理在代码中（3分）

        Args:
            content: SKILL.md 内容

        Returns:
            代码质量得分（0-15）
        """
        score = 0

        # 代码块数量和长度（8分）
        code_blocks = utils.extract_code_blocks(content)
        code_block_count = len(code_blocks)

        if code_block_count >= 5:
            score += 8
        elif code_block_count >= 3:
            score += 6
        elif code_block_count >= 2:
            score += 4
        elif code_block_count >= 1:
            score += 2

        # 安全性关键词（4分）
        security_keywords = self.keywords['security']

        if utils.check_keywords(content, security_keywords):
            security_count = utils.count_keyword_occurrences(content, security_keywords)
            if security_count >= 3:
                score += 4
            elif security_count >= 1:
                score += 2

        # 错误处理在代码中（3分）
        # 检查代码块中是否有 try/catch, error handling 等
        has_try_catch = 'try' in content.lower() and ('catch' in content.lower() or 'except' in content.lower())

        if has_try_catch:
            score += 3
        elif 'error' in content.lower():
            score += 1

        return min(score, self.weights['code_quality'])

    def _score_pattern_design(self, content: str) -> int:
        """
        评分：模式设计（10分）

        检查项：
        - 设计模式识别（6分）
        - 架构说明（4分）

        Args:
            content: SKILL.md 内容

        Returns:
            模式设计得分（0-10）
        """
        score = 0

        # 设计模式识别（6分）
        patterns = self._detect_patterns(content)
        pattern_count = len(patterns)

        if pattern_count >= 3:
            score += 6
        elif pattern_count >= 2:
            score += 4
        elif pattern_count >= 1:
            score += 2

        # 架构说明（4分）
        architecture_keywords = ['architecture', 'pattern', 'design', '架构', '设计']

        if utils.has_section(content, 'Architecture') or utils.has_section(content, 'Pattern'):
            score += 4
        elif utils.check_keywords(content, architecture_keywords):
            score += 2

        return min(score, self.weights['pattern_design'])

    def _score_error_handling(self, content: str) -> int:
        """
        评分：错误处理（5分）

        检查项：
        - 错误处理关键词（3分）
        - 错误处理章节（2分）

        Args:
            content: SKILL.md 内容

        Returns:
            错误处理得分（0-5）
        """
        score = 0

        # 错误处理关键词（3分）
        error_keywords = self.keywords['error_handling']

        if utils.check_keywords(content, error_keywords):
            error_count = utils.count_keyword_occurrences(content, error_keywords)
            if error_count >= 5:
                score += 3
            elif error_count >= 2:
                score += 2
            elif error_count >= 1:
                score += 1

        # 错误处理章节（2分）
        if utils.has_section(content, 'Error') or utils.has_section(content, 'Exception'):
            score += 2

        return min(score, self.weights['error_handling'])

    def _detect_patterns(self, content: str) -> List[str]:
        """
        检测设计模式

        Args:
            content: 文本内容

        Returns:
            检测到的设计模式列表
        """
        patterns_found = []
        pattern_keywords = self.keywords['patterns']

        for pattern in pattern_keywords:
            if pattern.lower() in content.lower():
                patterns_found.append(pattern)

        return patterns_found
