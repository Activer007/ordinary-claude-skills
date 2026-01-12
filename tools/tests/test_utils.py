"""
测试 utils.py 中的工具函数
"""
import pytest
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer import utils


class TestHasSection:
    """测试 has_section 函数"""

    def test_when_to_use_this_skill_variant(self, sample_markdown_with_when_to_use):
        """测试 'When to Use This Skill' 变体（这是 Bug 场景）"""
        # 这个测试在修复前会失败
        assert utils.has_section(sample_markdown_with_when_to_use, 'When to Use') == True

    def test_exact_match(self, sample_markdown_with_when_to_use):
        """测试精确匹配"""
        assert utils.has_section(sample_markdown_with_when_to_use, 'When to Use This Skill') == True

    def test_case_insensitive(self, sample_markdown_with_when_to_use):
        """测试大小写不敏感"""
        assert utils.has_section(sample_markdown_with_when_to_use, 'WHEN TO USE') == True
        assert utils.has_section(sample_markdown_with_when_to_use, 'quick start') == True

    def test_missing_section(self, sample_markdown_with_when_to_use):
        """测试不存在的章节"""
        assert utils.has_section(sample_markdown_with_when_to_use, 'Non-existent Section') == False

    def test_best_practices_variant(self, sample_markdown_with_when_to_use):
        """测试 'Best Practice' vs 'Best Practices'"""
        assert utils.has_section(sample_markdown_with_when_to_use, 'Best Practice') == True

    def test_quick_start_variants(self, sample_markdown_with_when_to_use):
        """测试 Quick Start 的多种变体"""
        assert utils.has_section(sample_markdown_with_when_to_use, 'Quick Start') == True
        assert utils.has_section(sample_markdown_with_when_to_use, 'Getting Started') == False  # 不在内容中


class TestCountCodeBlocks:
    """测试代码块统计"""

    def test_count_single_code_block(self, sample_markdown_with_when_to_use):
        """测试统计单个代码块"""
        count = utils.count_code_blocks(sample_markdown_with_when_to_use)
        assert count == 1

    def test_count_zero_code_blocks(self, sample_markdown_minimal):
        """测试无代码块的情况"""
        count = utils.count_code_blocks(sample_markdown_minimal)
        assert count == 0

    def test_multiple_code_blocks(self):
        """测试多个代码块"""
        content = """
# Test

```python
code1
```

Some text

```javascript
code2
```
"""
        count = utils.count_code_blocks(content)
        assert count == 2


class TestCountSections:
    """测试章节统计"""

    def test_count_sections(self, sample_markdown_with_when_to_use):
        """测试章节统计"""
        count = utils.count_sections(sample_markdown_with_when_to_use)
        # # My Skill, ## When to Use, ## Quick Start, ## Best Practices, ## Examples
        assert count == 5

    def test_different_heading_levels(self):
        """测试不同级别的标题"""
        content = """
# H1
## H2
### H3
#### H4
##### H5
###### H6
"""
        count = utils.count_sections(content)
        assert count == 6
