#!/usr/bin/env python3
"""
技术实现评分器（30分）

评分维度：
- 代码示例质量（15分）：代码正确性、安全性考虑、错误处理
- 模式设计（10分）：设计模式应用、架构合理性
- 错误处理（5分）：异常处理覆盖
"""

from typing import Dict, List, Union
from . import utils
from .skill_document import SkillDocument


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

    def score(self, content: Union[str, SkillDocument]) -> Dict:
        """
        计算技术实现评分

        Args:
            content: SKILL.md 内容（字符串）或 SkillDocument 对象

        Returns:
            评分结果字典
        """
        if isinstance(content, str):
            doc = None
            content_str = content
        else:
            doc = content
            content_str = doc.markdown_body

        code_quality_score = self._score_code_quality(content_str, doc)
        pattern_score = self._score_pattern_design(content_str, doc)
        error_handling_score = self._score_error_handling(content_str, doc)

        total = code_quality_score + pattern_score + error_handling_score

        # 提取详细信息
        if doc:
            code_blocks_count = len(doc.code_blocks)
            has_error_handling = any(b.has_error_handling for b in doc.code_blocks) or \
                                utils.check_keywords(content_str, self.keywords['error_handling'])
        else:
            code_blocks_count = utils.count_code_blocks(content_str)
            has_error_handling = utils.check_keywords(content_str, self.keywords['error_handling'])

        return {
            'total': total,
            'max': self.weights['total'],
            'code_quality': code_quality_score,
            'pattern_design': pattern_score,
            'error_handling': error_handling_score,
            'details': {
                'code_blocks_count': code_blocks_count,
                'has_security_keywords': utils.check_keywords(content_str, self.keywords['security']),
                'design_patterns_found': self._detect_patterns(content_str, doc),
                'has_error_handling': has_error_handling,
            }
        }

    def _score_code_quality(self, content: str, doc: SkillDocument = None) -> int:
        """
        评分：代码示例质量（15分）

        检查项：
        - 代码块数量和长度（8分）
        - 安全性关键词（4分）
        - 错误处理在代码中（3分）

        Args:
            content: SKILL.md 内容
            doc: SkillDocument 对象

        Returns:
            代码质量得分（0-15）
        """
        score = 0

        # 代码块数量和长度（8分）
        if doc:
            code_block_count = len(doc.code_blocks)
        else:
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
        if doc:
            has_try_catch = any(b.has_error_handling for b in doc.code_blocks)
        else:
            has_try_catch = 'try' in content.lower() and ('catch' in content.lower() or 'except' in content.lower())

        if has_try_catch:
            score += 3
        elif 'error' in content.lower():
            score += 1

        return min(score, self.weights['code_quality'])

    def _score_pattern_design(self, content: str, doc: SkillDocument = None) -> int:
        """
        评分：模式设计（10分）

        检查项：
        - 设计模式识别（6分）
        - 架构说明（4分）

        Args:
            content: SKILL.md 内容
            doc: SkillDocument 对象

        Returns:
            模式设计得分（0-10）
        """
        score = 0

        # 设计模式识别（6分）
        patterns = self._detect_patterns(content, doc)
        pattern_count = len(patterns)

        if pattern_count >= 3:
            score += 6
        elif pattern_count >= 2:
            score += 4
        elif pattern_count >= 1:
            score += 2

        # 架构说明（4分）
        architecture_keywords = ['architecture', 'pattern', 'design', '架构', '设计']

        if (doc and (doc.has_section('Architecture') or doc.has_section('Pattern'))) or \
           (not doc and (utils.has_section(content, 'Architecture') or utils.has_section(content, 'Pattern'))):
            score += 4
        elif utils.check_keywords(content, architecture_keywords):
            score += 2

        return min(score, self.weights['pattern_design'])

    def _score_error_handling(self, content: str, doc: SkillDocument = None) -> int:
        """
        评分：错误处理（5分）

        检查项：
        - 错误处理关键词（3分）
        - 错误处理章节（2分）

        Args:
            content: SKILL.md 内容
            doc: SkillDocument 对象

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
        if (doc and (doc.has_section('Error') or doc.has_section('Exception'))) or \
           (not doc and (utils.has_section(content, 'Error') or utils.has_section(content, 'Exception'))):
            score += 2

        return min(score, self.weights['error_handling'])

    def _detect_patterns(self, content: str, doc: SkillDocument = None) -> List[str]:
        """
        检测设计模式

        Args:
            content: 文本内容
            doc: SkillDocument 对象

        Returns:
            检测到的设计模式列表
        """
        patterns_found = set()
        pattern_keywords = self.keywords['patterns']

        # 在文档正文中搜索
        content_lower = content.lower()
        for pattern in pattern_keywords:
            if pattern.lower() in content_lower:
                patterns_found.add(pattern)

        # 在代码块中搜索
        if doc:
            for block in doc.code_blocks:
                block_content_lower = block.content.lower()
                for pattern in pattern_keywords:
                    if pattern.lower() in block_content_lower:
                        patterns_found.add(pattern)

        return list(patterns_found)
