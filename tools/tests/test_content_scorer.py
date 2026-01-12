"""
测试 content_scorer.py
"""
import pytest
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.content_scorer import ContentScorer


class TestContentScorer:
    """测试内容质量评分器"""

    @pytest.fixture
    def scorer(self, config):
        """创建评分器实例"""
        return ContentScorer(config)

    def test_score_with_when_to_use_section(self, scorer, sample_markdown_with_when_to_use):
        """测试包含 When to Use 章节的评分"""
        result = scorer.score(sample_markdown_with_when_to_use, {})

        # 验证检测到了 When to Use 章节
        assert result['details']['has_when_to_use'] == True

        # 验证指令清晰度得分大于 0
        assert result['clarity'] > 0

        # 验证总分在合理范围内
        assert 0 <= result['total'] <= 50

    def test_score_without_when_to_use(self, scorer, sample_markdown_minimal):
        """测试不包含 When to Use 章节的评分"""
        result = scorer.score(sample_markdown_minimal, {})

        # 验证未检测到 When to Use 章节
        assert result['details']['has_when_to_use'] == False

        # 验证总分低于包含 When to Use 的情况
        assert result['total'] < 20  # 应该得分很低

    def test_code_blocks_scoring(self, scorer):
        """测试代码块数量对评分的影响"""
        content_with_code = """
# Test Skill

## When to Use This Skill

- Use case 1
- Use case 2

```python
def example1():
    pass
```

```javascript
function example2() {}
```

```bash
echo "example3"
```
"""
        result = scorer.score(content_with_code, {})

        # 验证检测到了代码块
        assert result['details']['code_blocks_count'] == 3

        # 技术深度分应该较高（有3个代码块）
        assert result['technical_depth'] > 5
