"""
pytest 配置和共享 fixtures
"""
import pytest
from pathlib import Path


@pytest.fixture
def sample_markdown_with_when_to_use():
    """包含 'When to Use This Skill' 章节的示例 Markdown"""
    return """
# My Skill

## When to Use This Skill

- Building REST APIs
- Creating microservices
- Designing scalable systems

## Quick Start

Get started quickly...

## Best Practices

Follow these guidelines...

## Examples

```python
def hello():
    print("Hello, World!")
```
"""


@pytest.fixture
def sample_markdown_minimal():
    """最小化的 SKILL.md 示例"""
    return """
# Minimal Skill

Some content here.
"""


@pytest.fixture
def config():
    """加载测试用配置"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from analyzer import utils
    config_path = Path(__file__).parent.parent / 'config' / 'scoring_weights.json'
    return utils.load_config(config_path)
