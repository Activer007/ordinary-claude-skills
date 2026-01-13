#!/usr/bin/env python3
"""
分析 GitHub 上的技能

功能：
1. 从 GitHub URL 直接分析技能质量
2. 支持批量分析（从文件读取 URLs）
3. 自动缓存下载的技能
4. 生成详细的评分报告

使用方法：
    # 分析单个技能
    python scripts/analyze_github_skill.py https://github.com/.../skill-name

    # 批量分析（从文件读取）
    python scripts/analyze_github_skill.py --batch urls.txt

    # 清理缓存
    python scripts/analyze_github_skill.py --clear-cache

    # 显示帮助
    python scripts/analyze_github_skill.py --help
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer.github_fetcher import GitHubSkillFetcher


def print_separator(char='=', length=60):
    """打印分隔线"""
    print(char * length)


def analyze_single_url(url: str, output_file: str = None):
    """
    分析单个 GitHub URL

    Args:
        url: GitHub 技能 URL
        output_file: 输出 JSON 文件路径（可选）
    """
    print_separator()
    print(f"🔍 分析 GitHub 技能")
    print_separator()
    print(f"\nURL: {url}")
    print(f"\n开始分析...\n")

    try:
        # 创建分析器并执行分析
        analyzer = SkillAnalyzer.from_github_url(url)
        result = analyzer.analyze()

        # 检查是否有错误
        if 'error' in result:
            print(f"\n❌ 分析失败: {result['error']}\n")
            return None

        # 输出结果
        print_separator()
        print("📊 分析结果")
        print_separator()

        print(f"\n技能名称: {result['skill_name']}")
        print(f"本地路径: {result['skill_path']}")

        # 总分和等级
        print(f"\n{'='*40}")
        print(f"总分: {result['total_score']}/100")
        print(f"等级: {result['grade']}")
        print(f"{'='*40}\n")

        # 详细评分
        scores = result['scores']
        print("详细评分:")
        print(f"  ├─ 内容质量: {scores['content']['total']:2}/50")
        print(f"  ├─ 技术实现: {scores['technical']['total']:2}/30")
        print(f"  ├─ 维护性:   {scores['maintenance']['total']:2}/10")
        print(f"  └─ 用户体验: {scores['ux']['total']:2}/10")

        # 改进建议
        recommendations = result.get('recommendations', [])
        if recommendations:
            print(f"\n💡 改进建议 ({len(recommendations)} 项):")
            for i, rec in enumerate(recommendations, 1):
                print(f"  {i}. {rec}")
        else:
            print(f"\n✅ 太棒了！没有改进建议，技能质量很高。")

        # 保存 JSON 结果
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # 添加时间戳
            result['analyzed_at'] = datetime.now().isoformat()
            result['github_url'] = url

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            print(f"\n📁 结果已保存到: {output_path}")

        print()
        print_separator()

        return result

    except Exception as e:
        print(f"\n❌ 分析失败: {e}\n")
        import traceback
        traceback.print_exc()
        return None


def analyze_batch(file_path: Path, output_dir: str = None):
    """
    批量分析 URLs（从文件读取）

    Args:
        file_path: 包含 URLs 的文本文件
        output_dir: 输出目录（可选）
    """
    print_separator()
    print(f"📋 批量分析模式")
    print_separator()

    # 读取 URLs
    if not file_path.exists():
        print(f"\n❌ 文件不存在: {file_path}\n")
        return

    urls = file_path.read_text(encoding='utf-8').strip().split('\n')
    urls = [url.strip() for url in urls if url.strip() and not url.startswith('#')]

    if not urls:
        print(f"\n❌ 文件中没有有效的 URL\n")
        return

    print(f"\n从文件读取: {file_path}")
    print(f"共 {len(urls)} 个 URL\n")

    results = []
    failures = []

    # 逐个分析
    for i, url in enumerate(urls, 1):
        print_separator()
        print(f"[{i}/{len(urls)}] {url}")
        print_separator()

        result = analyze_single_url(url)

        if result and 'error' not in result:
            results.append(result)
            print(f"✅ 成功: {result['skill_name']} ({result['total_score']}/100)")
        else:
            failures.append({'url': url, 'error': result.get('error', 'Unknown error') if result else 'Download failed'})
            print(f"❌ 失败")

        print()

    # 汇总报告
    print_separator()
    print("📈 批量分析汇总")
    print_separator()

    print(f"\n总计: {len(urls)} 个 URL")
    print(f"成功: {len(results)} 个")
    print(f"失败: {len(failures)} 个")

    if results:
        scores = [r['total_score'] for r in results]
        grades = [r['grade'] for r in results]

        print(f"\n评分统计:")
        print(f"  平均分: {sum(scores)/len(scores):.1f}/100")
        print(f"  最高分: {max(scores)}/100")
        print(f"  最低分: {min(scores)}/100")

        print(f"\n等级分布:")
        for grade in ['S', 'A', 'B', 'C', 'D']:
            count = grades.count(grade)
            if count > 0:
                percentage = count / len(results) * 100
                print(f"  {grade} 级: {count} 个 ({percentage:.1f}%)")

        # Top 3
        sorted_results = sorted(results, key=lambda x: x['total_score'], reverse=True)
        print(f"\n🏆 Top 3 高分技能:")
        for i, r in enumerate(sorted_results[:3], 1):
            print(f"  {i}. {r['skill_name']} ({r['total_score']}/100 - {r['grade']})")

        # 保存批量结果
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            batch_file = output_path / f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'analyzed_at': datetime.now().isoformat(),
                    'total_count': len(urls),
                    'success_count': len(results),
                    'failure_count': len(failures),
                    'results': results,
                    'failures': failures
                }, f, indent=2, ensure_ascii=False)

            print(f"\n📁 批量结果已保存到: {batch_file}")

    if failures:
        print(f"\n⚠️  失败的 URL:")
        for f in failures:
            print(f"  - {f['url']}")
            print(f"    原因: {f['error']}")

    print()
    print_separator()


def clear_cache(skill_name: str = None):
    """
    清理缓存

    Args:
        skill_name: 指定技能名称，None 表示清理全部
    """
    print_separator()
    print("🗑️  清理缓存")
    print_separator()

    fetcher = GitHubSkillFetcher()

    if skill_name:
        print(f"\n清理技能: {skill_name}")
    else:
        print(f"\n清理全部缓存")

    fetcher.clear_cache(skill_name)
    print()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='分析 GitHub 上的技能质量',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 分析单个技能
  %(prog)s https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills/applying-brand-guidelines

  # 批量分析
  %(prog)s --batch urls.txt

  # 保存结果到 JSON
  %(prog)s <URL> --output result.json

  # 批量分析并保存
  %(prog)s --batch urls.txt --output-dir reports/

  # 清理全部缓存
  %(prog)s --clear-cache

  # 清理特定技能缓存
  %(prog)s --clear-cache --skill-name applying-brand-guidelines
        """
    )

    parser.add_argument('url', nargs='?', help='GitHub 技能 URL')
    parser.add_argument('--batch', type=Path, help='批量分析（从文件读取 URLs）')
    parser.add_argument('--output', help='输出 JSON 文件路径（单个分析）')
    parser.add_argument('--output-dir', help='输出目录（批量分析）')
    parser.add_argument('--clear-cache', action='store_true', help='清理缓存')
    parser.add_argument('--skill-name', help='指定技能名称（用于清理缓存）')

    args = parser.parse_args()

    # 清理缓存
    if args.clear_cache:
        clear_cache(args.skill_name)
        return

    # 批量分析
    if args.batch:
        analyze_batch(args.batch, args.output_dir)
        return

    # 单个分析
    if args.url:
        analyze_single_url(args.url, args.output)
        return

    # 没有参数，显示帮助
    parser.print_help()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  操作被用户中断\n")
        sys.exit(1)
