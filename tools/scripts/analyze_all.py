#!/usr/bin/env python3
"""
批量分析所有技能脚本
生成 JSON 报告和 Markdown 总结
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import List

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer.report_generator import ReportGenerator
from analyzer import utils


def analyze_all_skills(skills_dir: Path, config: dict, limit: int = None) -> List[dict]:
    """
    分析所有技能

    Args:
        skills_dir: 技能目录
        config: 配置字典
        limit: 限制分析数量（用于测试）

    Returns:
        分析结果列表
    """
    results = []

    # 获取所有技能目录
    skill_dirs = [d for d in skills_dir.iterdir() if d.is_dir()]

    if limit:
        skill_dirs = skill_dirs[:limit]

    total = len(skill_dirs)

    print(f"🔍 Found {total} skills in {skills_dir}")
    print("=" * 60)

    # 分析每个技能
    for i, skill_dir in enumerate(skill_dirs, 1):
        skill_name = skill_dir.name

        # 进度显示
        progress = f"[{i}/{total}]"
        print(f"{progress} Analyzing: {skill_name}...", end='')

        try:
            analyzer = SkillAnalyzer(skill_dir, config)
            result = analyzer.analyze()
            results.append(result)

            # 显示分数和等级
            if 'error' not in result:
                score = result['total_score']
                grade = result['grade']
                print(f" ✓ Score: {score} ({grade})")
            else:
                print(f" ✗ Error: {result.get('error', 'Unknown')}")

        except Exception as e:
            print(f" ✗ Exception: {str(e)}")
            results.append({
                'skill_name': skill_name,
                'skill_path': str(skill_dir),
                'error': str(e),
                'total_score': 0,
                'grade': 'ERROR',
            })

    print("=" * 60 + "\n")

    return results


def save_json_report(results: List[dict], output_dir: Path, duration: float) -> str:
    """
    保存 JSON 报告

    Args:
        results: 分析结果列表
        output_dir: 输出目录
        duration: 分析耗时

    Returns:
        JSON 文件路径
    """
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"analysis_{timestamp}.json"
    filepath = output_dir / filename

    # 统计数据
    valid_results = [r for r in results if 'error' not in r]
    total_skills = len(results)
    average_score = sum(r['total_score'] for r in valid_results) / len(valid_results) if valid_results else 0

    # 评分分布
    grade_dist = {'S': 0, 'A': 0, 'B': 0, 'C': 0, 'D': 0}
    for r in valid_results:
        grade = r.get('grade', 'D')
        if grade in grade_dist:
            grade_dist[grade] += 1

    # Top 10 和 Bottom 10
    top_10 = sorted(valid_results, key=lambda x: x['total_score'], reverse=True)[:10]
    bottom_10 = sorted(valid_results, key=lambda x: x['total_score'])[:10]

    # 简化 Top/Bottom（只保留关键信息）
    top_10_simple = [
        {
            'skill_name': r['skill_name'],
            'score': r['total_score'],
            'grade': r['grade'],
            'path': r['skill_path']
        }
        for r in top_10
    ]

    bottom_10_simple = [
        {
            'skill_name': r['skill_name'],
            'score': r['total_score'],
            'grade': r['grade'],
            'path': r['skill_path']
        }
        for r in bottom_10
    ]

    # 构建报告
    report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'total_skills': total_skills,
            'analysis_duration': round(duration, 2),
        },
        'summary': {
            'average_score': round(average_score, 1),
            'grade_distribution': grade_dist,
        },
        'top_10_skills': top_10_simple,
        'bottom_10_skills': bottom_10_simple,
        'detailed_results': results,
    }

    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    return str(filepath)


def save_markdown_summary(results: List[dict], output_dir: Path, duration: float, config: dict) -> str:
    """
    保存 Markdown 总结

    Args:
        results: 分析结果列表
        output_dir: 输出目录
        duration: 分析耗时
        config: 配置字典

    Returns:
        Markdown 文件路径
    """
    # 生成文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"summary_{timestamp}.md"
    filepath = output_dir / filename

    # 生成 Markdown 内容
    generator = ReportGenerator(config)
    markdown_content = generator.generate_summary(results, duration)

    # 保存文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(markdown_content)

    return str(filepath)


def main():
    """主函数"""
    # 参数解析
    skills_dir = Path(__file__).parent.parent.parent / 'skills_all'
    limit = None

    if '--limit' in sys.argv:
        try:
            idx = sys.argv.index('--limit')
            limit = int(sys.argv[idx + 1])
        except (IndexError, ValueError):
            print("❌ Error: --limit requires an integer argument")
            sys.exit(1)

    if not skills_dir.exists():
        print(f"❌ Error: Skills directory not found: {skills_dir}")
        sys.exit(1)

    # 加载配置
    config_path = Path(__file__).parent.parent / 'config' / 'scoring_weights.json'
    config = utils.load_config(config_path)

    # 输出目录
    output_dir = Path(__file__).parent.parent / 'reports'
    output_dir.mkdir(exist_ok=True)

    # 开始分析
    print("\n📊 Skills 批量质量分析工具\n")
    start_time = time.time()

    results = analyze_all_skills(skills_dir, config, limit)

    duration = time.time() - start_time

    # 保存报告
    print("📄 Generating reports...")

    json_path = save_json_report(results, output_dir, duration)
    print(f"  ✓ JSON report: {json_path}")

    md_path = save_markdown_summary(results, output_dir, duration, config)
    print(f"  ✓ Markdown summary: {md_path}")

    print("\n✅ Analysis complete!")
    print(f"⏱️  Total time: {int(duration // 60)}m {int(duration % 60)}s\n")


if __name__ == '__main__':
    main()
