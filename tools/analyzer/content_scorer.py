#!/usr/bin/env python3
"""
内容质量评分器（50分）⭐ 权重最高

评分维度：
- 指令清晰度（13分）：检测 "When to Use" 章节、使用场景描述
- 技术深度（19分）：代码示例数量、最佳实践说明
- 文档完整度（13分）：章节结构、示例覆盖、陷阱说明
- 可操作性（5分）：step-by-step 指导
"""

from typing import Dict, Union, Optional
import re
from . import utils
from .skill_document import SkillDocument
from .scoring_utils import smooth_score
from .config_loader import ScoringConfig, get_config


class ContentScorer:
    """内容质量评分器"""

    def __init__(self, config: Dict, scoring_config: Optional[ScoringConfig] = None):
        """
        初始化评分器

        Args:
            config: 配置字典（权重和关键词）
            scoring_config: 评分参数配置（可选，默认使用全局配置）
        """
        self.config = config
        self.weights = config['weights']['content_quality']
        self.keywords = config['keywords']

        # 加载评分参数配置
        self.scoring_config = scoring_config or get_config()

    def score(self, content: Union[str, SkillDocument], metadata: Dict) -> Dict:
        """
        计算内容质量评分

        Args:
            content: SKILL.md 内容（字符串）或 SkillDocument 对象
            metadata: metadata.json 数据

        Returns:
            评分结果字典
        """
        # 兼容旧接口：如果传入字符串，则转换为 SkillDocument
        if isinstance(content, str):
            # 为了向后兼容，仍然支持字符串输入
            # 但这会失去预处理的性能优势
            doc = None
            content_str = content
        else:
            doc = content
            content_str = doc.markdown_body

        clarity_score = self._score_clarity(content_str, doc)
        depth_score = self._score_technical_depth(content_str, doc)
        doc_score = self._score_documentation(content_str, doc)
        action_score = self._score_actionability(content_str, doc)

        total = clarity_score + depth_score + doc_score + action_score

        # 提取详细信息（使用预处理数据或回退到旧方法）
        if doc:
            has_when_to_use = doc.has_section('When to Use')
            code_blocks_count = len(doc.code_blocks)
            sections_count = len(doc.sections)
        else:
            has_when_to_use = utils.has_section(content_str, 'When to Use')
            code_blocks_count = utils.count_code_blocks(content_str)
            sections_count = utils.count_sections(content_str)

        return {
            'total': total,
            'max': self.weights['total'],
            'clarity': clarity_score,
            'technical_depth': depth_score,
            'documentation': doc_score,
            'actionability': action_score,
            'details': {
                'has_when_to_use': has_when_to_use,
                'use_cases_count': len(utils.extract_use_cases(content_str)),
                'code_blocks_count': code_blocks_count,
                'sections_count': sections_count,
                'has_best_practices': utils.check_keywords(content_str, self.keywords['best_practices']),
                'has_step_by_step': utils.has_step_by_step(content_str),
            }
        }

    def _score_clarity(self, content: str, doc: SkillDocument = None) -> int:
        """
        评分：指令清晰度（13分）

        检查项：
        - 是否有 "When to Use" 章节（5分）
        - 使用场景数量（5分，3个以上满分）
        - 场景描述清晰度（3分）

        Args:
            content: SKILL.md 内容
            doc: SkillDocument 对象（可选，提供预处理数据）

        Returns:
            指令清晰度得分（0-13）
        """
        score = 0

        # 检查 "When to Use" 章节（5分）
        # 优先使用预处理数据
        if doc:
            has_when_to_use = doc.has_section('When to Use')
        else:
            has_when_to_use = utils.has_section(content, 'When to Use')

        if has_when_to_use:
            score += 5
        elif utils.check_keywords(content, self.keywords['when_to_use']):
            score += 3  # 有相关关键词但没有专门章节

        # 使用场景数量（5分）
        use_cases = utils.extract_use_cases(content)
        use_case_count = len(use_cases)
        params = self.scoring_config.get_smooth_params('content_quality', 'clarity', 'use_cases')
        score += smooth_score(use_case_count, **params)

        # 场景描述清晰度（3分）
        # 检查是否有具体的动词（designing, creating, implementing等）
        action_verbs = ['design', 'create', 'implement', 'build', 'develop',
                       'refactor', 'migrate', 'optimize', '设计', '创建', '实现']
        if utils.check_keywords(content, action_verbs):
            score += 3

        return min(score, self.weights['clarity'])

    def _score_technical_depth(self, content: str, doc: SkillDocument = None) -> int:
        """
        评分：技术深度（19分）

        检查项：
        - 代码示例数量（7分）
        - 最佳实践说明（5分）
        - 设计模式或架构说明（4分）
        - 输入/输出示例配对（3分）

        Args:
            content: SKILL.md 内容
            doc: SkillDocument 对象（可选，提供预处理数据）

        Returns:
            技术深度得分（0-19）
        """
        score = 0

        # 代码示例数量（7分）
        # 优先使用预处理数据
        if doc:
            code_blocks = len(doc.code_blocks)
        else:
            code_blocks = utils.count_code_blocks(content)

        # 调整为满分7分 (>=5 -> 7, >=3 -> 5, >=1 -> 2)
        params = self.scoring_config.get_smooth_params('content_quality', 'technical_depth', 'code_blocks')
        score += smooth_score(code_blocks, **params)

        # 最佳实践说明（5分）
        if doc:
            has_best_practice = doc.has_section('Best Practice')
        else:
            has_best_practice = utils.has_section(content, 'Best Practice')

        if has_best_practice:
            score += 5
        elif utils.check_keywords(content, self.keywords['best_practices']):
            best_practice_count = utils.count_keyword_occurrences(
                content, self.keywords['best_practices']
            )
            # 使用平滑评分，最多得 4 分（有专门章节得 5 分）
            params = self.scoring_config.get_smooth_params('content_quality', 'technical_depth', 'best_practices')
            score += smooth_score(best_practice_count, **params)

        # 设计模式或架构说明（4分）
        if doc:
            has_pattern = doc.has_section('Pattern') or doc.has_section('Architecture')
        else:
            has_pattern = utils.has_section(content, 'Pattern') or utils.has_section(content, 'Architecture')

        if has_pattern:
            score += 4
        elif utils.check_keywords(content, self.keywords['patterns']):
            score += 2

        # 输入/输出示例配对（3分）
        score += self._score_input_output_examples(content)

        return min(score, self.weights['technical_depth'])

    def _score_input_output_examples(self, content: str) -> int:
        """
        评分：输入/输出示例配对（3分）
        """
        patterns = [
            r'input\s*:.*?\n\s*output\s*:',
            r'request\s*:.*?\n\s*response\s*:',
            r'before\s*:.*?\n\s*after\s*:',
            r'>>>\s+', # Python REPL style
        ]
        
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
                return 3
        return 0

    def _score_documentation(self, content: str, doc: SkillDocument = None) -> int:
        """
        评分：文档完整度（13分）

        检查项：
        - 章节结构（6分，6个以上满分）
        - 示例覆盖（4分）
        - 常见陷阱/注意事项（3分）

        Args:
            content: SKILL.md 内容
            doc: SkillDocument 对象（可选，提供预处理数据）

        Returns:
            文档完整度得分（0-13）
        """
        score = 0

        # 章节结构（6分）
        # 优先使用预处理数据
        if doc:
            sections_count = len(doc.sections)
        else:
            sections_count = utils.count_sections(content)

        params = self.scoring_config.get_smooth_params('content_quality', 'documentation', 'sections')
        score += smooth_score(sections_count, **params)

        # 示例覆盖（4分）
        if doc:
            has_example = doc.has_section('Example')
        else:
            has_example = utils.has_section(content, 'Example')

        if not has_example:
            has_example = 'example' in content.lower()

        if has_example:
            example_count = content.lower().count('example')
            params = self.scoring_config.get_smooth_params('content_quality', 'documentation', 'examples')
            score += smooth_score(example_count, **params)

        # 常见陷阱/注意事项（3分）
        pitfall_keywords = ['pitfall', 'common mistake', 'avoid', 'caution',
                           'warning', 'note', '陷阱', '注意', '避免']

        if doc:
            has_pitfall = doc.has_section('Pitfall') or doc.has_section('Common Mistake')
        else:
            has_pitfall = utils.has_section(content, 'Pitfall') or \
                          utils.has_section(content, 'Common Mistake')

        if has_pitfall:
            score += 3
        elif utils.check_keywords(content, pitfall_keywords):
            score += 2

        return min(score, self.weights['documentation'])

    def _score_actionability(self, content: str, doc: SkillDocument = None) -> int:
        """
        评分：可操作性（5分）

        检查项：
        - Step-by-step 指导（3分）
        - 具体的代码示例（2分）

        Args:
            content: SKILL.md 内容
            doc: SkillDocument 对象（可选，提供预处理数据）

        Returns:
            可操作性得分（0-5）
        """
        score = 0

        # Step-by-step 指导（3分）
        if utils.has_step_by_step(content):
            score += 3

        # 具体的代码示例（2分）
        # 优先使用预处理数据
        if doc:
            code_blocks = len(doc.code_blocks)
        else:
            code_blocks = utils.count_code_blocks(content)

        if code_blocks > 0:
            score += 2

        return min(score, self.weights['actionability'])
