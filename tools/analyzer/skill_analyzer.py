#!/usr/bin/env python3
"""
Skill 质量分析器主类
协调所有评分器，生成最终分析报告
"""

from pathlib import Path
from typing import Dict, List, Optional
from . import utils
from .content_scorer import ContentScorer
from .technical_scorer import TechnicalScorer
from .maintenance_scorer import MaintenanceScorer
from .ux_scorer import UXScorer
from .skill_document import SkillDocument


class SkillAnalyzer:
    """Skill 质量分析器"""

    def __init__(self, skill_path: Path, config: Dict):
        """
        初始化分析器

        Args:
            skill_path: 技能目录路径
            config: 配置字典
        """
        self.skill_path = Path(skill_path)
        self.skill_name = self.skill_path.name
        self.config = config

        # 初始化评分器
        self.content_scorer = ContentScorer(config)
        self.technical_scorer = TechnicalScorer(config)
        self.maintenance_scorer = MaintenanceScorer(config)
        self.ux_scorer = UXScorer(config)

    @classmethod
    def from_github_url(cls, url: str, config: Optional[Dict] = None, cache_dir: Optional[Path] = None, force_refresh: bool = False):
        """
        从 GitHub URL 创建分析器

        Args:
            url: GitHub 仓库 URL
                格式: https://github.com/user/repo/tree/branch/path/to/skill
            config: 配置字典，默认自动加载
            cache_dir: 缓存目录，默认为系统临时目录
            force_refresh: 是否强制重新下载（忽略缓存）

        Returns:
            SkillAnalyzer 实例

        Raises:
            ValueError: 如果 URL 格式无效
            requests.exceptions.RequestException: 如果下载失败
            FileNotFoundError: 如果 SKILL.md 不存在

        Example:
            >>> analyzer = SkillAnalyzer.from_github_url(
            ...     "https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills/applying-brand-guidelines"
            ... )
            >>> result = analyzer.analyze()
        """
        from .github_fetcher import GitHubSkillFetcher

        # 加载默认配置（使用更可靠的路径解析）
        if config is None:
            # 使用 resolve() 获取绝对路径，避免相对路径问题
            config_dir = Path(__file__).resolve().parent.parent / 'config'
            config_path = config_dir / 'scoring_weights.json'
            config = utils.load_config(config_path)

        # 下载技能（传递 force_refresh 参数）
        fetcher = GitHubSkillFetcher(cache_dir)
        skill_path = fetcher.download_skill(url, force_refresh=force_refresh)

        # 创建并返回分析器实例
        return cls(skill_path, config)

    def analyze(self) -> Dict:
        """
        执行完整分析

        Returns:
            分析结果字典
        """
        try:
            # 使用 SkillDocument 进行统一预处理
            doc = SkillDocument(self.skill_path)
            markdown_content = doc.markdown_body
            metadata = doc.metadata
            yaml_metadata = doc.yaml_frontmatter

            # 执行评分
            content_score = self.content_scorer.score(doc, metadata)
            technical_score = self.technical_scorer.score(doc)
            maintenance_score = self.maintenance_scorer.score(metadata, markdown_content)
            ux_score = self.ux_scorer.score(doc)

            # 计算总分
            total_score = (
                content_score['total'] +
                technical_score['total'] +
                maintenance_score['total'] +
                ux_score['total']
            )

            # 计算等级
            grade = self._get_grade(total_score)

            # 生成改进建议
            recommendations = self._generate_recommendations(
                content_score, technical_score, maintenance_score, ux_score
            )

            return {
                'skill_name': self.skill_name,
                'skill_path': str(self.skill_path),
                'total_score': total_score,
                'grade': grade,
                'scores': {
                    'content': content_score,
                    'technical': technical_score,
                    'maintenance': maintenance_score,
                    'ux': ux_score,
                },
                'metadata': metadata,
                'yaml_metadata': yaml_metadata,
                'recommendations': recommendations,
            }

        except Exception as e:
            # 错误处理
            return {
                'skill_name': self.skill_name,
                'skill_path': str(self.skill_path),
                'error': str(e),
                'total_score': 0,
                'grade': 'ERROR',
            }

    def _get_grade(self, total_score: int) -> str:
        """
        根据总分计算等级

        Args:
            total_score: 总分

        Returns:
            等级 (S/A/B/C/D)
        """
        thresholds = self.config['grade_thresholds']

        if total_score >= thresholds['S']:
            return 'S'
        elif total_score >= thresholds['A']:
            return 'A'
        elif total_score >= thresholds['B']:
            return 'B'
        elif total_score >= thresholds['C']:
            return 'C'
        else:
            return 'D'

    def _generate_recommendations(
        self,
        content_score: Dict,
        technical_score: Dict,
        maintenance_score: Dict,
        ux_score: Dict
    ) -> List[str]:
        """
        生成改进建议

        Args:
            content_score: 内容质量评分
            technical_score: 技术实现评分
            maintenance_score: 维护性评分
            ux_score: 用户体验评分

        Returns:
            改进建议列表
        """
        recommendations = []

        # 内容质量建议
        if not content_score['details']['has_when_to_use']:
            recommendations.append("添加 'When to Use' 章节，明确使用场景")

        if content_score['details']['use_cases_count'] < 3:
            recommendations.append("增加使用场景描述（建议至少3个）")

        if content_score['details']['code_blocks_count'] < 3:
            recommendations.append("增加代码示例（建议至少3个）")

        if not content_score['details']['has_best_practices']:
            recommendations.append("添加最佳实践说明")

        # 技术实现建议
        if not technical_score['details']['has_security_keywords']:
            recommendations.append("添加安全性考虑说明（输入验证、权限控制等）")

        if len(technical_score['details']['design_patterns_found']) == 0:
            recommendations.append("添加设计模式或架构说明")

        if not technical_score['details']['has_error_handling']:
            recommendations.append("完善错误处理示例和说明")

        # 维护性建议
        if maintenance_score['details']['days_since_update']:
            days = maintenance_score['details']['days_since_update']
            if days > 180:
                recommendations.append(f"技能已 {days} 天未更新，建议更新内容")

        if not maintenance_score['details']['has_version_info']:
            recommendations.append("添加版本兼容性说明")

        # 用户体验建议
        if not ux_score['details']['has_quick_start']:
            recommendations.append("添加 'Quick Start' 或 'Getting Started' 章节")

        if ux_score['details']['sections_count'] < 4:
            recommendations.append("改进文档结构，增加章节划分")

        return recommendations
