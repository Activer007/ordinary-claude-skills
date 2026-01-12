#!/usr/bin/env python3
"""
技能对比分析脚本
对比多个技能的评分细节，识别重复技能
"""

import sys
from pathlib import Path
from difflib import SequenceMatcher

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer import utils


def calculate_similarity(str1: str, str2: str) -> float:
    """
    计算两个字符串的相似度

    Args:
        str1: 字符串1
        str2: 字符串2

    Returns:
        相似度（0.0-1.0）
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def print_comparison_table(results: list):
    """
    打印对比表格

    Args:
        results: 分析结果列表
    """
    print("\n" + "=" * 100)
    print("📊 Skills 对比分析报告")
    print("=" * 100 + "\n")

    # 表头
    print(f"{'Skill Name':<30} {'Total':<8} {'Grade':<8} {'Content':<10} {'Technical':<10} {'Maint':<8} {'UX':<6}")
    print("-" * 100)

    # 各个技能的评分
    for result in results:
        if 'error' in result:
            name = result['skill_name']
            print(f"{name:<30} {'ERROR':<8} {'-':<8} {'-':<10} {'-':<10} {'-':<8} {'-':<6}")
        else:
            name = result['skill_name']
            total = result['total_score']
            grade = result['grade']

            scores = result['scores']
            content = f"{scores['content']['total']}/50"
            technical = f"{scores['technical']['total']}/30"
            maintenance = f"{scores['maintenance']['total']}/10"
            ux = f"{scores['ux']['total']}/10"

            print(f"{name:<30} {total:<8} {grade:<8} {content:<10} {technical:<10} {maintenance:<8} {ux:<6}")

    print("=" * 100 + "\n")


def print_similarity_analysis(skill_names: list):
    """
    打印名称相似度分析

    Args:
        skill_names: 技能名称列表
    """
    if len(skill_names) < 2:
        return

    print("🔍 名称相似度分析\n")

    for i in range(len(skill_names)):
        for j in range(i + 1, len(skill_names)):
            similarity = calculate_similarity(skill_names[i], skill_names[j])

            if similarity > 0.5:  # 相似度超过 50%
                print(f"  {skill_names[i]} <-> {skill_names[j]}: {similarity*100:.1f}%")

                if similarity > 0.8:
                    print(f"    ⚠️  高度相似，可能是重复技能")

    print()


def print_recommendations(results: list):
    """
    打印推荐建议

    Args:
        results: 分析结果列表
    """
    valid_results = [r for r in results if 'error' not in r]

    if not valid_results:
        return

    # 找出最佳技能
    best = max(valid_results, key=lambda x: x['total_score'])

    print("💡 推荐建议\n")
    print(f"  📌 推荐使用: {best['skill_name']} ({best['total_score']}分, {best['grade']}级)")

    # 分析差异
    if len(valid_results) > 1:
        worst = min(valid_results, key=lambda x: x['total_score'])

        if best != worst:
            score_diff = best['total_score'] - worst['total_score']
            print(f"  📊 最大分差: {score_diff}分")

            # 分析优势
            best_scores = best['scores']
            worst_scores = worst['scores']

            print(f"\n  {best['skill_name']} 的优势:")

            if best_scores['content']['total'] > worst_scores['content']['total']:
                diff = best_scores['content']['total'] - worst_scores['content']['total']
                print(f"    • 内容质量高 {diff}分")

            if best_scores['technical']['total'] > worst_scores['technical']['total']:
                diff = best_scores['technical']['total'] - worst_scores['technical']['total']
                print(f"    • 技术实现好 {diff}分")

    print()


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("Usage: python compare_skills.py <skill1> <skill2> [skill3] ...")
        print("\nExample:")
        print("  python compare_skills.py pdf pdf-processing pdf-processing-pro")
        print("\nNote: Skill names will be searched in ../skills_all/")
        sys.exit(1)

    skill_names = sys.argv[1:]

    if len(skill_names) > 5:
        print("❌ Error: Maximum 5 skills can be compared at once")
        sys.exit(1)

    # 技能目录
    skills_dir = Path(__file__).parent.parent.parent / 'skills_all'

    if not skills_dir.exists():
        print(f"❌ Error: Skills directory not found: {skills_dir}")
        sys.exit(1)

    # 加载配置
    config_path = Path(__file__).parent.parent / 'config' / 'scoring_weights.json'
    config = utils.load_config(config_path)

    # 分析每个技能
    results = []

    print(f"\n🔍 Comparing {len(skill_names)} skills...\n")

    for skill_name in skill_names:
        skill_path = skills_dir / skill_name

        if not skill_path.exists():
            print(f"  ✗ {skill_name}: Not found")
            results.append({
                'skill_name': skill_name,
                'error': 'Skill not found',
                'total_score': 0,
                'grade': 'ERROR',
            })
            continue

        print(f"  ✓ {skill_name}: Analyzing...", end='')

        try:
            analyzer = SkillAnalyzer(skill_path, config)
            result = analyzer.analyze()
            results.append(result)

            if 'error' not in result:
                print(f" Done ({result['total_score']} points)")
            else:
                print(f" Error: {result['error']}")

        except Exception as e:
            print(f" Exception: {str(e)}")
            results.append({
                'skill_name': skill_name,
                'error': str(e),
                'total_score': 0,
                'grade': 'ERROR',
            })

    # 打印对比表格
    print_comparison_table(results)

    # 打印相似度分析
    print_similarity_analysis(skill_names)

    # 打印推荐建议
    print_recommendations(results)


if __name__ == '__main__':
    main()
