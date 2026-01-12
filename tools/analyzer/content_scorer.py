#!/usr/bin/env python3
"""
内容质量评分器（50分）⭐ 权重最高

评分维度：
- 指令清晰度（13分）：检测 "When to Use" 章节、使用场景描述
- 技术深度（19分）：代码示例数量、最佳实践说明
- 文档完整度（13分）：章节结构、示例覆盖、陷阱说明
- 可操作性（5分）：step-by-step 指导
"""

from typing import Dict
from . import utils


class ContentScorer:
    """内容质量评分器"""

    def __init__(self, config: Dict):
        """
        初始化评分器

        Args:
            config: 配置字典
        """
        self.config = config
        self.weights = config['weights']['content_quality']
        self.keywords = config['keywords']

    def score(self, content: str, metadata: Dict) -> Dict:
        """
        计算内容质量评分

        Args:
            content: SKILL.md 内容
            metadata: metadata.json 数据

        Returns:
            评分结果字典
        """
        clarity_score = self._score_clarity(content)
        depth_score = self._score_technical_depth(content)
        doc_score = self._score_documentation(content)
        action_score = self._score_actionability(content)

        total = clarity_score + depth_score + doc_score + action_score

        return {
            'total': total,
            'max': self.weights['total'],
            'clarity': clarity_score,
            'technical_depth': depth_score,
            'documentation': doc_score,
            'actionability': action_score,
            'details': {
                'has_when_to_use': utils.has_section(content, 'When to Use'),
                'use_cases_count': len(utils.extract_use_cases(content)),
                'code_blocks_count': utils.count_code_blocks(content),
                'sections_count': utils.count_sections(content),
                'has_best_practices': utils.check_keywords(content, self.keywords['best_practices']),
                'has_step_by_step': utils.has_step_by_step(content),
            }
        }

    def _score_clarity(self, content: str) -> int:
        """
        评分：指令清晰度（13分）

        检查项：
        - 是否有 "When to Use" 章节（5分）
        - 使用场景数量（5分，3个以上满分）
        - 场景描述清晰度（3分）

        Args:
            content: SKILL.md 内容

        Returns:
            指令清晰度得分（0-13）
        """
        score = 0

        # 检查 "When to Use" 章节（5分）
        if utils.has_section(content, 'When to Use'):
            score += 5
        elif utils.check_keywords(content, self.keywords['when_to_use']):
            score += 3  # 有相关关键词但没有专门章节

        # 使用场景数量（5分）
        use_cases = utils.extract_use_cases(content)
        use_case_count = len(use_cases)

        if use_case_count >= 5:
            score += 5
        elif use_case_count >= 3:
            score += 4
        elif use_case_count >= 2:
            score += 3
        elif use_case_count >= 1:
            score += 2

        # 场景描述清晰度（3分）
        # 检查是否有具体的动词（designing, creating, implementing等）
        action_verbs = ['design', 'create', 'implement', 'build', 'develop',
                       'refactor', 'migrate', 'optimize', '设计', '创建', '实现']
        if utils.check_keywords(content, action_verbs):
            score += 3

        return min(score, self.weights['clarity'])

    def _score_technical_depth(self, content: str) -> int:
        """
        评分：技术深度（19分）

        检查项：
        - 代码示例数量（10分，5个以上满分）
        - 最佳实践说明（5分）
        - 设计模式或架构说明（4分）

        Args:
            content: SKILL.md 内容

        Returns:
            技术深度得分（0-19）
        """
        score = 0

        # 代码示例数量（10分）
        code_blocks = utils.count_code_blocks(content)

        if code_blocks >= 5:
            score += 10
        elif code_blocks >= 3:
            score += 7
        elif code_blocks >= 2:
            score += 5
        elif code_blocks >= 1:
            score += 3

        # 最佳实践说明（5分）
        if utils.has_section(content, 'Best Practice'):
            score += 5
        elif utils.check_keywords(content, self.keywords['best_practices']):
            best_practice_count = utils.count_keyword_occurrences(
                content, self.keywords['best_practices']
            )
            if best_practice_count >= 3:
                score += 4
            elif best_practice_count >= 1:
                score += 2

        # 设计模式或架构说明（4分）
        if utils.has_section(content, 'Pattern') or utils.has_section(content, 'Architecture'):
            score += 4
        elif utils.check_keywords(content, self.keywords['patterns']):
            score += 2

        return min(score, self.weights['technical_depth'])

    def _score_documentation(self, content: str) -> int:
        """
        评分：文档完整度（13分）

        检查项：
        - 章节结构（6分，6个以上满分）
        - 示例覆盖（4分）
        - 常见陷阱/注意事项（3分）

        Args:
            content: SKILL.md 内容

        Returns:
            文档完整度得分（0-13）
        """
        score = 0

        # 章节结构（6分）
        sections_count = utils.count_sections(content)

        if sections_count >= 6:
            score += 6
        elif sections_count >= 4:
            score += 4
        elif sections_count >= 2:
            score += 2

        # 示例覆盖（4分）
        has_example = utils.has_section(content, 'Example') or \
                      'example' in content.lower()

        if has_example:
            example_count = content.lower().count('example')
            if example_count >= 3:
                score += 4
            elif example_count >= 1:
                score += 2

        # 常见陷阱/注意事项（3分）
        pitfall_keywords = ['pitfall', 'common mistake', 'avoid', 'caution',
                           'warning', 'note', '陷阱', '注意', '避免']

        if utils.has_section(content, 'Pitfall') or \
           utils.has_section(content, 'Common Mistake'):
            score += 3
        elif utils.check_keywords(content, pitfall_keywords):
            score += 2

        return min(score, self.weights['documentation'])

    def _score_actionability(self, content: str) -> int:
        """
        评分：可操作性（5分）

        检查项：
        - Step-by-step 指导（3分）
        - 具体的代码示例（2分）

        Args:
            content: SKILL.md 内容

        Returns:
            可操作性得分（0-5）
        """
        score = 0

        # Step-by-step 指导（3分）
        if utils.has_step_by_step(content):
            score += 3

        # 具体的代码示例（2分）
        code_blocks = utils.count_code_blocks(content)
        if code_blocks > 0:
            score += 2

        return min(score, self.weights['actionability'])
