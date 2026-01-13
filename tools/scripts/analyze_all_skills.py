#!/usr/bin/env python3
"""
全量技能评分分析脚本

功能：
1. 扫描 skills_all/ 目录下的所有技能（415个）
2. 对每个技能进行质量评分
3. 生成详细的分析报告（JSON 和 Markdown 格式）
4. 生成 Top 100 高分技能推荐列表
5. 生成待改进技能清单（低分技能）

使用方法：
    cd tools
    source .venv/bin/activate
    python scripts/analyze_all_skills.py

Created: 2026-01-13
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, date
from typing import List, Dict, Any
from collections import defaultdict


class DateTimeEncoder(json.JSONEncoder):
    """自定义 JSON 编码器，处理 datetime 和 date 对象"""
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        return super().default(obj)

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer import utils


class SkillBatchAnalyzer:
    """批量技能分析器"""

    def __init__(self, skills_dir: Path, output_dir: Path):
        """
        初始化批量分析器

        Args:
            skills_dir: 技能目录路径（skills_all/）
            output_dir: 输出目录路径（reports/）
        """
        self.skills_dir = skills_dir
        self.output_dir = output_dir

        # 加载配置字典
        config_path = Path(__file__).parent.parent / 'config' / 'scoring_weights.json'
        self.config = utils.load_config(config_path)

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 统计信息
        self.total_skills = 0
        self.analyzed_skills = 0
        self.failed_skills = 0
        self.start_time = None

        # 结果存储
        self.results: List[Dict[str, Any]] = []
        self.failed: List[Dict[str, str]] = []

    def discover_skills(self) -> List[Path]:
        """
        扫描并发现所有技能目录

        Returns:
            技能路径列表
        """
        print(f"📂 扫描技能目录: {self.skills_dir}")

        skills = []
        for item in sorted(self.skills_dir.iterdir()):
            if item.is_dir() and not item.name.startswith('.'):
                # 检查是否包含 SKILL.md
                skill_md = item / 'SKILL.md'
                if skill_md.exists():
                    skills.append(item)
                else:
                    print(f"⚠️  跳过（缺少 SKILL.md）: {item.name}")

        self.total_skills = len(skills)
        print(f"✅ 发现 {self.total_skills} 个有效技能\n")
        return skills

    def analyze_skill(self, skill_path: Path) -> Dict[str, Any]:
        """
        分析单个技能

        Args:
            skill_path: 技能路径

        Returns:
            分析结果字典
        """
        try:
            analyzer = SkillAnalyzer(skill_path, self.config)
            result = analyzer.analyze()

            # 添加技能名称和路径
            result['skill_name'] = skill_path.name
            result['skill_path'] = str(skill_path.relative_to(self.skills_dir.parent))

            return result
        except Exception as e:
            raise Exception(f"分析失败: {str(e)}")

    def run_analysis(self, max_skills: int = None) -> None:
        """
        运行批量分析

        Args:
            max_skills: 最大分析数量（用于测试，None表示全部）
        """
        print("=" * 80)
        print("🚀 开始批量技能分析")
        print("=" * 80)

        self.start_time = time.time()

        # 发现技能
        skills = self.discover_skills()

        if max_skills:
            skills = skills[:max_skills]
            print(f"⚠️  测试模式：仅分析前 {max_skills} 个技能\n")

        # 分析每个技能
        print(f"📊 开始分析 {len(skills)} 个技能...\n")

        for i, skill_path in enumerate(skills, 1):
            skill_name = skill_path.name

            try:
                # 显示进度
                print(f"[{i}/{len(skills)}] 分析中: {skill_name}", end=" ... ")

                # 执行分析
                result = self.analyze_skill(skill_path)

                # 保存结果
                self.results.append(result)
                self.analyzed_skills += 1

                # 显示结果
                score = result['total_score']
                grade = result['grade']
                print(f"✅ {score}/100 ({grade}级)")

            except Exception as e:
                self.failed_skills += 1
                self.failed.append({
                    'skill_name': skill_name,
                    'skill_path': str(skill_path.relative_to(self.skills_dir.parent)),
                    'error': str(e)
                })
                print(f"❌ 失败: {str(e)}")

        # 完成统计
        elapsed_time = time.time() - self.start_time
        print("\n" + "=" * 80)
        print("✅ 分析完成！")
        print("=" * 80)
        print(f"📊 统计信息:")
        print(f"  - 总技能数: {len(skills)}")
        print(f"  - 成功分析: {self.analyzed_skills}")
        print(f"  - 分析失败: {self.failed_skills}")
        print(f"  - 耗时: {elapsed_time:.2f} 秒")
        print(f"  - 平均速度: {elapsed_time/len(skills):.2f} 秒/技能")
        print("=" * 80 + "\n")

    def generate_statistics(self) -> Dict[str, Any]:
        """
        生成统计信息

        Returns:
            统计信息字典
        """
        if not self.results:
            return {}

        scores = [r['total_score'] for r in self.results]
        grades = [r['grade'] for r in self.results]

        # 评分分布
        grade_distribution = defaultdict(int)
        for grade in grades:
            grade_distribution[grade] += 1

        # 评分区间分布
        score_ranges = {
            '90-100 (S级)': 0,
            '80-89 (A级)': 0,
            '70-79 (B级)': 0,
            '60-69 (C级)': 0,
            '0-59 (D级)': 0
        }
        for score in scores:
            if score >= 90:
                score_ranges['90-100 (S级)'] += 1
            elif score >= 80:
                score_ranges['80-89 (A级)'] += 1
            elif score >= 70:
                score_ranges['70-79 (B级)'] += 1
            elif score >= 60:
                score_ranges['60-69 (C级)'] += 1
            else:
                score_ranges['0-59 (D级)'] += 1

        return {
            'total_skills': len(self.results),
            'successful_analysis': self.analyzed_skills,
            'failed_analysis': self.failed_skills,
            'average_score': sum(scores) / len(scores),
            'median_score': sorted(scores)[len(scores) // 2],
            'min_score': min(scores),
            'max_score': max(scores),
            'grade_distribution': dict(grade_distribution),
            'score_ranges': score_ranges,
            'timestamp': datetime.now().isoformat(),
            'elapsed_time': time.time() - self.start_time if self.start_time else 0
        }

    def save_json_report(self) -> Path:
        """
        保存 JSON 格式的完整报告

        Returns:
            报告文件路径
        """
        report_path = self.output_dir / 'skills_analysis_full_report.json'

        report = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'skills_directory': str(self.skills_dir),
                'total_skills': self.total_skills,
                'analyzed_skills': self.analyzed_skills,
                'failed_skills': self.failed_skills
            },
            'statistics': self.generate_statistics(),
            'results': self.results,
            'failed': self.failed
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, cls=DateTimeEncoder)

        print(f"💾 已保存 JSON 报告: {report_path}")
        return report_path

    def save_markdown_summary(self) -> Path:
        """
        保存 Markdown 格式的可读报告

        Returns:
            报告文件路径
        """
        report_path = self.output_dir / 'skills_analysis_summary.md'

        stats = self.generate_statistics()

        # 构建 Markdown 内容
        lines = [
            "# 📊 Skills 质量分析报告",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            "",
            "## 📈 总体统计",
            "",
            f"- **分析技能总数**: {stats['total_skills']}",
            f"- **成功分析**: {stats['successful_analysis']}",
            f"- **失败分析**: {stats['failed_analysis']}",
            f"- **平均分**: {stats['average_score']:.1f}/100",
            f"- **中位数分**: {stats['median_score']}/100",
            f"- **最高分**: {stats['max_score']}/100",
            f"- **最低分**: {stats['min_score']}/100",
            f"- **分析耗时**: {stats['elapsed_time']:.2f} 秒",
            "",
            "---",
            "",
            "## 🏆 评分等级分布",
            "",
            "| 等级 | 分数范围 | 数量 | 占比 |",
            "|------|----------|------|------|",
        ]

        # 添加评分等级分布
        total = stats['total_skills']
        for grade in ['S', 'A', 'B', 'C', 'D']:
            count = stats['grade_distribution'].get(grade, 0)
            percentage = (count / total * 100) if total > 0 else 0

            score_range = {
                'S': '90-100',
                'A': '80-89',
                'B': '70-79',
                'C': '60-69',
                'D': '0-59'
            }[grade]

            lines.append(f"| {grade} 级 | {score_range} | {count} | {percentage:.1f}% |")

        lines.extend([
            "",
            "---",
            "",
            "## 📊 评分区间分布",
            "",
        ])

        # 添加评分区间可视化
        for range_name, count in stats['score_ranges'].items():
            percentage = (count / total * 100) if total > 0 else 0
            bar_length = int(percentage / 2)  # 每2%一个字符
            bar = '█' * bar_length
            lines.append(f"**{range_name}**: {count} ({percentage:.1f}%)")
            lines.append(f"```\n{bar}\n```")
            lines.append("")

        lines.extend([
            "---",
            "",
            "## 🔝 Top 10 高分技能",
            "",
            "| 排名 | 技能名称 | 评分 | 等级 |",
            "|------|----------|------|------|",
        ])

        # 添加 Top 10
        sorted_results = sorted(self.results, key=lambda x: x['total_score'], reverse=True)
        for i, result in enumerate(sorted_results[:10], 1):
            lines.append(
                f"| {i} | {result['skill_name']} | {result['total_score']}/100 | {result['grade']} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## ⚠️ Bottom 10 低分技能",
            "",
            "| 排名 | 技能名称 | 评分 | 等级 |",
            "|------|----------|------|------|",
        ])

        # 添加 Bottom 10
        for i, result in enumerate(sorted_results[-10:][::-1], 1):
            lines.append(
                f"| {i} | {result['skill_name']} | {result['total_score']}/100 | {result['grade']} |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## 📋 详细信息",
            "",
            f"完整的详细分析数据请查看: [`skills_analysis_full_report.json`](skills_analysis_full_report.json)",
            "",
        ])

        # 如果有失败的技能，添加失败列表
        if self.failed:
            lines.extend([
                "---",
                "",
                f"## ❌ 分析失败的技能 ({len(self.failed)})",
                "",
                "| 技能名称 | 错误信息 |",
                "|----------|----------|",
            ])

            for failure in self.failed:
                lines.append(f"| {failure['skill_name']} | {failure['error']} |")

            lines.append("")

        lines.extend([
            "---",
            "",
            f"*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])

        # 写入文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"📝 已保存 Markdown 报告: {report_path}")
        return report_path

    def save_top_skills(self, top_n: int = 100) -> Path:
        """
        保存高分技能推荐列表

        Args:
            top_n: 前N个技能

        Returns:
            报告文件路径
        """
        report_path = self.output_dir / 'top_100_skills.md'

        # 按评分排序
        sorted_results = sorted(self.results, key=lambda x: x['total_score'], reverse=True)
        top_skills = sorted_results[:top_n]

        lines = [
            f"# 🏆 Top {min(top_n, len(top_skills))} 高分技能推荐",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "本列表根据质量评分系统自动生成，推荐高质量的 Skills 供使用。",
            "",
            "---",
            "",
            "## 📋 推荐列表",
            "",
            "| 排名 | 技能名称 | 评分 | 等级 | 路径 |",
            "|------|----------|------|------|------|",
        ]

        for i, result in enumerate(top_skills, 1):
            skill_name = result['skill_name']
            score = result['total_score']
            grade = result['grade']
            path = result['skill_path']

            lines.append(f"| {i} | {skill_name} | {score}/100 | {grade} | `{path}` |")

        lines.extend([
            "",
            "---",
            "",
            "## 📊 统计信息",
            "",
        ])

        # 统计等级分布
        grade_counts = {}
        for result in top_skills:
            grade = result['grade']
            grade_counts[grade] = grade_counts.get(grade, 0) + 1

        lines.append("**等级分布**:")
        lines.append("")
        for grade in ['S', 'A', 'B', 'C', 'D']:
            count = grade_counts.get(grade, 0)
            if count > 0:
                percentage = (count / len(top_skills) * 100)
                lines.append(f"- {grade} 级: {count} ({percentage:.1f}%)")

        lines.extend([
            "",
            f"**平均分**: {sum(r['total_score'] for r in top_skills) / len(top_skills):.1f}/100",
            "",
            "---",
            "",
            "## 💡 使用建议",
            "",
            "1. **S级技能** (90-100分): 顶级质量，强烈推荐使用",
            "2. **A级技能** (80-89分): 优秀质量，推荐使用",
            "3. **B级技能** (70-79分): 良好质量，可以使用",
            "",
            "---",
            "",
            f"*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"🏆 已保存 Top {min(top_n, len(top_skills))} 技能列表: {report_path}")
        return report_path

    def save_improvement_candidates(self, threshold: int = 60) -> Path:
        """
        保存待改进技能清单

        Args:
            threshold: 评分阈值（低于此分数的技能）

        Returns:
            报告文件路径
        """
        report_path = self.output_dir / 'improvement_candidates.md'

        # 筛选低分技能
        low_score_skills = [r for r in self.results if r['total_score'] < threshold]
        low_score_skills.sort(key=lambda x: x['total_score'])

        lines = [
            f"# ⚠️ 待改进技能清单 (评分 < {threshold})",
            "",
            f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"本列表包含 {len(low_score_skills)} 个评分低于 {threshold} 分的技能，建议进行优化改进。",
            "",
            "---",
            "",
            "## 📋 待改进列表",
            "",
            "| 排名 | 技能名称 | 当前评分 | 等级 | 主要问题 | 路径 |",
            "|------|----------|----------|------|----------|------|",
        ]

        for i, result in enumerate(low_score_skills, 1):
            skill_name = result['skill_name']
            score = result['total_score']
            grade = result['grade']
            path = result['skill_path']

            # 分析主要问题
            issues = []
            scores = result.get('scores', {})

            # 检查内容质量
            content_score = scores.get('content', {}).get('total', 0)
            if content_score < 25:  # 低于50%
                issues.append("内容质量低")

            # 检查技术实现
            technical_score = scores.get('technical', {}).get('total', 0)
            if technical_score < 15:  # 低于50%
                issues.append("技术实现弱")

            # 检查文档完整性
            content_details = scores.get('content', {}).get('details', {})
            if not content_details.get('has_when_to_use', False):
                issues.append("缺少使用场景")

            if content_details.get('code_blocks_count', 0) < 3:
                issues.append("代码示例不足")

            main_issue = "、".join(issues) if issues else "综合质量需提升"

            lines.append(f"| {i} | {skill_name} | {score}/100 | {grade} | {main_issue} | `{path}` |")

        lines.extend([
            "",
            "---",
            "",
            "## 📊 问题分析",
            "",
        ])

        # 统计常见问题
        problem_stats = {
            "缺少使用场景": 0,
            "代码示例不足": 0,
            "内容质量低": 0,
            "技术实现弱": 0
        }

        for result in low_score_skills:
            scores = result.get('scores', {})
            content_details = scores.get('content', {}).get('details', {})

            if not content_details.get('has_when_to_use', False):
                problem_stats["缺少使用场景"] += 1

            if content_details.get('code_blocks_count', 0) < 3:
                problem_stats["代码示例不足"] += 1

            if scores.get('content', {}).get('total', 0) < 25:
                problem_stats["内容质量低"] += 1

            if scores.get('technical', {}).get('total', 0) < 15:
                problem_stats["技术实现弱"] += 1

        lines.append("**常见问题统计**:")
        lines.append("")
        for problem, count in problem_stats.items():
            if count > 0:
                percentage = (count / len(low_score_skills) * 100) if low_score_skills else 0
                lines.append(f"- {problem}: {count} ({percentage:.1f}%)")

        lines.extend([
            "",
            "---",
            "",
            "## 💡 改进建议",
            "",
            "### 快速提升评分的方法",
            "",
            "1. **添加 'When to Use' 章节** (+5-10分)",
            "   - 明确列出 3-5 个使用场景",
            "   - 说明适用条件和不适用场景",
            "",
            "2. **增加代码示例** (+5-10分)",
            "   - 至少提供 3 个完整的代码示例",
            "   - 代码应包含注释说明",
            "   - 展示实际应用场景",
            "",
            "3. **完善文档结构** (+3-5分)",
            "   - 添加清晰的章节标题",
            "   - 补充快速开始指南",
            "   - 增加最佳实践说明",
            "",
            "4. **增强技术深度** (+5-8分)",
            "   - 说明设计模式或架构考虑",
            "   - 添加安全性相关说明",
            "   - 提供错误处理示例",
            "",
            "---",
            "",
            "## 📈 预期效果",
            "",
            "通过以上改进，大多数技能可以从 D级 提升到 C级 或 B级：",
            "",
            "- D级 (< 60分) → C级 (60-69分): 补充基础内容",
            "- C级 (60-69分) → B级 (70-79分): 优化示例和文档",
            "- B级 (70-79分) → A级 (80-89分): 深化技术内容",
            "",
            "---",
            "",
            f"*报告生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
            ""
        ])

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"⚠️  已保存待改进技能清单: {report_path}")
        return report_path


def main():
    """主函数"""
    # 配置路径
    project_root = Path(__file__).parent.parent.parent
    skills_dir = project_root / 'skills_all'
    output_dir = project_root / 'reports'

    # 检查目录是否存在
    if not skills_dir.exists():
        print(f"❌ 错误: 技能目录不存在: {skills_dir}")
        sys.exit(1)

    # 创建分析器
    analyzer = SkillBatchAnalyzer(skills_dir, output_dir)

    # 运行完整分析（全部 415 个技能）
    analyzer.run_analysis()

    # 生成所有报告
    print("\n📝 生成报告...")
    analyzer.save_json_report()
    analyzer.save_markdown_summary()
    analyzer.save_top_skills(top_n=100)
    analyzer.save_improvement_candidates(threshold=60)

    print("\n🎉 全部完成！")
    print(f"\n📁 报告文件位于: {output_dir}")
    print("   - skills_analysis_full_report.json  (完整JSON数据)")
    print("   - skills_analysis_summary.md        (可读分析报告)")
    print("   - top_100_skills.md                 (高分技能推荐)")
    print("   - improvement_candidates.md         (待改进技能)")


if __name__ == '__main__':
    main()
