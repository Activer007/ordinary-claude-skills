#!/usr/bin/env python3
"""
Markdown 报告生成器
根据分析结果生成可读的 Markdown 总结报告
"""

from typing import Dict, List
from datetime import datetime


class ReportGenerator:
    """Markdown 报告生成器"""

    def __init__(self, config: Dict):
        """
        初始化报告生成器

        Args:
            config: 配置字典
        """
        self.config = config

    def generate_summary(self, analysis_results: List[Dict], duration: float) -> str:
        """
        生成批量分析的 Markdown 总结报告

        Args:
            analysis_results: 分析结果列表
            duration: 分析耗时（秒）

        Returns:
            Markdown 格式的总结报告
        """
        # 过滤错误结果
        valid_results = [r for r in analysis_results if 'error' not in r]
        error_results = [r for r in analysis_results if 'error' in r]

        # 统计数据
        total_skills = len(analysis_results)
        valid_count = len(valid_results)
        average_score = sum(r['total_score'] for r in valid_results) / valid_count if valid_count > 0 else 0

        # 评分分布
        grade_dist = self._calculate_grade_distribution(valid_results)

        # Top 10 和 Bottom 10
        top_10 = sorted(valid_results, key=lambda x: x['total_score'], reverse=True)[:10]
        bottom_10 = sorted(valid_results, key=lambda x: x['total_score'])[:10]

        # 生成报告
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        lines = [
            "# Skills 质量评估报告\n",
            f"生成时间：{timestamp}\n",
            "## 📊 总体统计\n",
            f"- 总技能数：{total_skills}",
            f"- 成功分析：{valid_count}",
            f"- 分析失败：{len(error_results)}",
            f"- 平均分：{average_score:.1f}",
            f"- 分析耗时：{minutes} 分钟 {seconds} 秒\n",
            "## 🏆 评分分布\n",
            "| 等级 | 分数范围 | 数量 | 占比 |",
            "|------|----------|------|------|",
        ]

        # 评分分布表格
        for grade in ['S', 'A', 'B', 'C', 'D']:
            count = grade_dist.get(grade, 0)
            percentage = (count / valid_count * 100) if valid_count > 0 else 0
            score_range = self._get_score_range(grade)
            lines.append(f"| {grade}级  | {score_range} | {count}   | {percentage:.1f}% |")

        lines.append("")

        # Top 10
        lines.extend([
            "## ⭐ Top 10 高质量技能\n",
        ])

        for i, result in enumerate(top_10, 1):
            score = result['total_score']
            grade = result['grade']
            name = result['skill_name']
            lines.append(f"{i}. **{name}** - {score}分 ({grade}级)")

        lines.append("")

        # Bottom 10
        lines.extend([
            "## ⚠️ Bottom 10 需改进技能\n",
        ])

        for i, result in enumerate(bottom_10, 1):
            score = result['total_score']
            grade = result['grade']
            name = result['skill_name']
            lines.append(f"{i}. **{name}** - {score}分 ({grade}级)")

        lines.append("")

        # 总体建议
        lines.extend(self._generate_overall_recommendations(valid_results))

        # 错误技能列表
        if error_results:
            lines.extend([
                "## ❌ 分析失败的技能\n",
            ])
            for result in error_results:
                lines.append(f"- {result['skill_name']}: {result.get('error', '未知错误')}")
            lines.append("")

        # 报告文件链接
        lines.append("---\n")
        lines.append("详细数据请查看 JSON 报告文件。\n")

        return "\n".join(lines)

    def _calculate_grade_distribution(self, results: List[Dict]) -> Dict[str, int]:
        """
        计算评分分布

        Args:
            results: 分析结果列表

        Returns:
            评分分布字典 {grade: count}
        """
        distribution = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}

        for result in results:
            grade = result.get('grade', 'D')
            if grade in distribution:
                distribution[grade] += 1

        return distribution

    def _get_score_range(self, grade: str) -> str:
        """
        获取等级对应的分数范围

        Args:
            grade: 等级

        Returns:
            分数范围字符串
        """
        thresholds = self.config['grade_thresholds']

        if grade == 'S':
            return "90-100"
        elif grade == 'A':
            return "80-89"
        elif grade == 'B':
            return "70-79"
        elif grade == 'C':
            return "60-69"
        else:
            return "<60"

    def _generate_overall_recommendations(self, results: List[Dict]) -> List[str]:
        """
        生成总体改进建议

        Args:
            results: 分析结果列表

        Returns:
            建议文本行列表
        """
        lines = ["## 💡 总体建议\n"]

        # 统计低分技能
        low_score_count = sum(1 for r in results if r['total_score'] < 70)
        total = len(results)
        low_score_pct = (low_score_count / total * 100) if total > 0 else 0

        if low_score_count > 0:
            lines.append(f"- {low_score_count}个技能（{low_score_pct:.1f}%）得分低于70分，建议重点优化")

        # 统计常见问题
        missing_when_to_use = 0
        missing_best_practices = 0
        few_examples = 0

        for result in results:
            if 'scores' in result:
                content_details = result['scores']['content']['details']
                if not content_details.get('has_when_to_use', False):
                    missing_when_to_use += 1
                if not content_details.get('has_best_practices', False):
                    missing_best_practices += 1
                if content_details.get('code_blocks_count', 0) < 3:
                    few_examples += 1

        if missing_when_to_use > 0:
            pct = (missing_when_to_use / total * 100)
            lines.append(f"- 主要问题：{missing_when_to_use}个技能（{pct:.1f}%）缺少 'When to Use' 章节")

        if missing_best_practices > total * 0.5:
            lines.append("- 建议：超过半数技能缺少最佳实践说明，建议补充")

        if few_examples > total * 0.3:
            lines.append("- 建议：约三分之一技能代码示例不足，建议增加到3个以上")

        # 平均分分析
        avg_content = sum(r['scores']['content']['total'] for r in results if 'scores' in r) / total if total > 0 else 0
        avg_technical = sum(r['scores']['technical']['total'] for r in results if 'scores' in r) / total if total > 0 else 0

        lines.append(f"- 建议优先改进：内容质量（平均得分 {avg_content:.1f}/50）")

        lines.append("")

        return lines
