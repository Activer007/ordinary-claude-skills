"""
测试章节匹配逻辑的准确性
验证词边界匹配，避免误匹配
"""
import pytest
import sys
from pathlib import Path
from dataclasses import dataclass

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_document import Section


class TestSectionMatching:
    """测试 Section.matches 方法的准确性"""

    def test_exact_match(self):
        """测试精确匹配"""
        section = Section(title="When to Use", level=2, content="", start_line=1, end_line=5)

        assert section.matches("When to Use") == True
        assert section.matches("when to use") == True  # 不区分大小写
        assert section.matches("WHEN TO USE") == True

    def test_partial_match_should_succeed(self):
        """测试部分匹配 - 应该成功的情况"""
        # "When to Use" 应该匹配包含它的标题
        section = Section(
            title="When to Use This Skill",
            level=2,
            content="",
            start_line=1,
            end_line=5
        )

        assert section.matches("When to Use") == True
        assert section.matches("Use") == True
        assert section.matches("This Skill") == True

    def test_word_boundary_prevents_false_positives(self):
        """测试词边界防止误匹配"""
        # "Use" 不应该匹配 "Reuse"
        section = Section(
            title="Reuse Patterns",
            level=2,
            content="",
            start_line=1,
            end_line=5
        )

        # "Use" 不应该匹配 "Reuse Patterns"，因为 "use" 是 "Reuse" 的一部分
        assert section.matches("Use") == False
        assert section.matches("Reuse") == True
        assert section.matches("Patterns") == True
        assert section.matches("Reuse Patterns") == True

    def test_common_skill_sections(self):
        """测试常见的技能章节名称"""
        test_cases = [
            ("When to Use This Skill", "When to Use", True),
            ("Quick Start Guide", "Quick Start", True),
            ("Best Practices", "Best Practices", True),
            ("Getting Started", "Quick Start", False),  # 不同的词汇
            ("Examples and Use Cases", "Examples", True),
            ("Examples and Use Cases", "Use Cases", True),
        ]

        for title, search_name, expected in test_cases:
            section = Section(title=title, level=2, content="", start_line=1, end_line=5)
            result = section.matches(search_name)
            assert result == expected, f"'{title}' 匹配 '{search_name}' 应该是 {expected}，实际是 {result}"

    def test_avoid_substring_false_positives(self):
        """测试避免子串误匹配"""
        test_cases = [
            ("Misuse Cases", "Use", False),  # "Use" 是 "Misuse" 的一部分
            ("Database Usage", "Use", False),  # "Use" 是 "Usage" 的一部分
            ("User Guide", "Use", False),  # "Use" 是 "User" 的一部分
            ("Useful Tips", "Use", False),  # "Use" 是 "Useful" 的一部分
            ("Reusable Components", "Use", False),  # "Use" 是 "Reusable" 的一部分
        ]

        for title, search_name, expected in test_cases:
            section = Section(title=title, level=2, content="", start_line=1, end_line=5)
            result = section.matches(search_name)
            assert result == expected, f"'{title}' 匹配 '{search_name}' 应该是 {expected}，实际是 {result}"

    def test_multi_word_matching(self):
        """测试多词匹配"""
        section = Section(
            title="API Design Best Practices",
            level=2,
            content="",
            start_line=1,
            end_line=5
        )

        assert section.matches("API") == True
        assert section.matches("Design") == True
        assert section.matches("Best Practices") == True
        assert section.matches("API Design") == True
        assert section.matches("Design Best") == True  # 连续的词

        # 不连续的词不应该匹配
        # 注意：当前实现只检查搜索词是否作为连续的单词出现
        assert section.matches("API Practices") == False  # 不连续

    def test_special_characters_in_title(self):
        """测试标题中的特殊字符"""
        test_cases = [
            ("What's New", "What's", True),
            ("How-to Guide", "How-to", True),
            ("Step-by-Step Tutorial", "Step-by-Step", True),
            ("FAQ (Frequently Asked Questions)", "FAQ", True),
            ("Core Concepts & Patterns", "Concepts", True),
            ("Core Concepts & Patterns", "Patterns", True),
        ]

        for title, search_name, expected in test_cases:
            section = Section(title=title, level=2, content="", start_line=1, end_line=5)
            result = section.matches(search_name)
            assert result == expected, f"'{title}' 匹配 '{search_name}' 应该是 {expected}，实际是 {result}"

    def test_case_insensitivity(self):
        """测试大小写不敏感"""
        section = Section(
            title="Quick Start",
            level=2,
            content="",
            start_line=1,
            end_line=5
        )

        assert section.matches("quick start") == True
        assert section.matches("Quick Start") == True
        assert section.matches("QUICK START") == True
        assert section.matches("QuIcK sTaRt") == True

    def test_empty_and_whitespace(self):
        """测试空字符串和空白字符"""
        section = Section(
            title="Normal Title",
            level=2,
            content="",
            start_line=1,
            end_line=5
        )

        # 空字符串不应该匹配
        assert section.matches("") == False

        # 只有空白的字符串不应该匹配
        assert section.matches("   ") == False

    def test_single_word_sections(self):
        """测试单词章节"""
        test_cases = [
            ("Examples", "Examples", True),
            ("Examples", "Example", False),  # 不完全匹配
            ("Installation", "Installation", True),
            ("Installation", "Install", False),  # 部分单词
            ("Usage", "Usage", True),
            ("Usage", "Use", False),  # 部分单词
        ]

        for title, search_name, expected in test_cases:
            section = Section(title=title, level=2, content="", start_line=1, end_line=5)
            result = section.matches(search_name)
            assert result == expected, f"'{title}' 匹配 '{search_name}' 应该是 {expected}，实际是 {result}"

    def test_numbers_in_title(self):
        """测试标题中的数字"""
        test_cases = [
            ("Top 10 Tips", "Top 10", True),
            ("Top 10 Tips", "10", True),
            ("Version 2.0 Features", "Version 2.0", True),
            ("Version 2.0 Features", "2.0", True),
            ("5 Common Mistakes", "5", True),
        ]

        for title, search_name, expected in test_cases:
            section = Section(title=title, level=2, content="", start_line=1, end_line=5)
            result = section.matches(search_name)
            assert result == expected, f"'{title}' 匹配 '{search_name}' 应该是 {expected}，实际是 {result}"

    def test_comprehensive_false_positive_prevention(self):
        """综合测试防止误匹配"""
        # 这是最重要的测试：确保误匹配率 < 5%

        # 不应该匹配的情况（预期 False）
        false_cases = [
            ("Reuse Patterns", "Use"),           # Use 是 Reuse 的一部分
            ("Misuse Cases", "Use"),             # Use 是 Misuse 的一部分
            ("User Guide", "Use"),               # Use 是 User 的一部分
            ("Database Usage", "Use"),           # Use 是 Usage 的一部分
            ("Useful Tips", "Use"),              # Use 是 Useful 的一部分
            ("Understanding the Basics", "Stand"),  # Stand 是 Understanding 的一部分
            ("Overview", "View"),                # View 是 Overview 的一部分
            ("Implementation Details", "Implement"),  # 部分单词
            ("Configuration", "Figure"),         # 部分单词
            ("Troubleshooting", "Shoot"),        # 部分单词
        ]

        false_positive_count = 0
        total_false_cases = len(false_cases)

        for title, search_name in false_cases:
            section = Section(title=title, level=2, content="", start_line=1, end_line=5)
            result = section.matches(search_name)
            if result == True:
                false_positive_count += 1
                print(f"\n❌ 误匹配: '{title}' 不应该匹配 '{search_name}'")

        # 计算误匹配率
        false_positive_rate = (false_positive_count / total_false_cases) * 100

        print(f"\n误匹配统计:")
        print(f"  总测试用例: {total_false_cases}")
        print(f"  误匹配数量: {false_positive_count}")
        print(f"  误匹配率: {false_positive_rate:.1f}%")

        # 验证误匹配率 < 5%
        assert false_positive_rate < 5.0, f"误匹配率 {false_positive_rate:.1f}% 超过 5% 的阈值"

    def test_true_positive_coverage(self):
        """测试正确匹配的覆盖率"""
        # 应该匹配的情况（预期 True）
        true_cases = [
            ("When to Use This Skill", "When to Use"),
            ("Quick Start Guide", "Quick Start"),
            ("Best Practices", "Best Practices"),
            ("API Design Principles", "API"),
            ("Error Handling Strategies", "Error Handling"),
            ("Installation and Setup", "Installation"),
            ("Examples and Use Cases", "Examples"),
            ("Frequently Asked Questions", "Questions"),
            ("Core Concepts", "Core"),
            ("Advanced Usage", "Advanced"),
        ]

        false_negative_count = 0
        total_true_cases = len(true_cases)

        for title, search_name in true_cases:
            section = Section(title=title, level=2, content="", start_line=1, end_line=5)
            result = section.matches(search_name)
            if result == False:
                false_negative_count += 1
                print(f"\n❌ 漏匹配: '{title}' 应该匹配 '{search_name}'")

        # 计算漏匹配率
        false_negative_rate = (false_negative_count / total_true_cases) * 100

        print(f"\n漏匹配统计:")
        print(f"  总测试用例: {total_true_cases}")
        print(f"  漏匹配数量: {false_negative_count}")
        print(f"  漏匹配率: {false_negative_rate:.1f}%")

        # 验证漏匹配率应该是 0%（所有应该匹配的都要匹配）
        assert false_negative_rate == 0.0, f"漏匹配率 {false_negative_rate:.1f}% 应该是 0%"
