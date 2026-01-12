#!/usr/bin/env python3
"""
单个技能分析脚本
"""

import sys
import json
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer import utils


def print_analysis_result(result: dict):
    """
    打印分析结果到终端

    Args:
        result: 分析结果字典
    """
    if 'error' in result:
        print(f"\n❌ 分析失败: {result['skill_name']}")
        print(f"错误: {result['error']}\n")
        return

    print("\n" + "=" * 60)
    print("📊 Skill 质量分析报告")
    print("=" * 60 + "\n")

    print(f"📁 Skill: {result['skill_name']}")
    print(f"📍 Path: {result['skill_path']}")
    print(f"🎯 Total Score: {result['total_score']}/100 (Grade: {result['grade']})\n")

    # 评分细节
    scores = result['scores']

    print(f"📝 Content Quality:      {scores['content']['total']}/{scores['content']['max']}  ⭐")
    print(f"🔧 Technical:            {scores['technical']['total']}/{scores['technical']['max']}")
    print(f"🔄 Maintenance:          {scores['maintenance']['total']}/{scores['maintenance']['max']}")
    print(f"👤 User Experience:      {scores['ux']['total']}/{scores['ux']['max']}\n")

    # 改进建议
    if result['recommendations']:
        print("=" * 60)
        print("💡 Recommendations")
        print("=" * 60 + "\n")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"{i}. {rec}")
        print()

    print("=" * 60 + "\n")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage: python analyze_single.py <skill_path>")
        print("\nExample:")
        print("  python analyze_single.py ../skills_all/api-design-principles")
        sys.exit(1)

    skill_path = Path(sys.argv[1])

    if not skill_path.exists():
        print(f"❌ Error: Skill path does not exist: {skill_path}")
        sys.exit(1)

    if not skill_path.is_dir():
        print(f"❌ Error: Path is not a directory: {skill_path}")
        sys.exit(1)

    # 加载配置
    config_path = Path(__file__).parent.parent / 'config' / 'scoring_weights.json'
    config = utils.load_config(config_path)

    # 执行分析
    print(f"🔍 Analyzing skill: {skill_path.name}...")

    analyzer = SkillAnalyzer(skill_path, config)
    result = analyzer.analyze()

    # 打印结果
    print_analysis_result(result)

    # 可选：保存 JSON 结果
    if '--json' in sys.argv:
        output_file = f"{result['skill_name']}_analysis.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"📄 JSON report saved to: {output_file}\n")


if __name__ == '__main__':
    main()
