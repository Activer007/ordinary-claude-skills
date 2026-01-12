"""
测试 SkillDocument 预处理层
"""
import pytest
import sys
from pathlib import Path
from dataclasses import dataclass

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_document import SkillDocument, Section, CodeBlock


class TestSkillDocumentBasics:
    """测试 SkillDocument 基础功能"""

    @pytest.fixture
    def temp_skill(self, tmp_path):
        """创建临时技能目录"""
        skill_dir = tmp_path / "test-skill"
        skill_dir.mkdir()

        # 创建 SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""---
name: test-skill
description: A test skill for unit testing
---

# Test Skill

## When to Use This Skill

- Use case 1
- Use case 2
- Use case 3

## Quick Start

Get started with this command:

```bash
npm install test-skill
```

## Examples

```python
def example():
    print("Hello from test skill")
    return 42
```

```javascript
function greet() {
    console.log("Hello, World!");
}
```

## Best Practices

Follow these guidelines for best results.
""")

        # 创建 metadata.json
        metadata_json = skill_dir / "metadata.json"
        metadata_json.write_text("""{
    "id": "test-skill-123",
    "name": "test-skill",
    "author": "test-author",
    "description": "Test skill description",
    "githubUrl": "https://github.com/test/test-skill"
}""")

        return skill_dir

    def test_load_content(self, temp_skill):
        """测试加载 SKILL.md 内容"""
        doc = SkillDocument(temp_skill)

        # 验证能加载内容
        assert doc.raw_content is not None
        assert len(doc.raw_content) > 0
        assert "Test Skill" in doc.raw_content

    def test_load_metadata(self, temp_skill):
        """测试加载 metadata.json"""
        doc = SkillDocument(temp_skill)

        # 验证能加载元数据
        assert doc.metadata is not None
        assert doc.metadata['id'] == 'test-skill-123'
        assert doc.metadata['name'] == 'test-skill'
        assert doc.metadata['author'] == 'test-author'

    def test_parse_yaml_frontmatter(self, temp_skill):
        """测试解析 YAML 前置元数据"""
        doc = SkillDocument(temp_skill)

        # 验证 YAML frontmatter 被正确解析
        assert doc.yaml_frontmatter is not None
        assert doc.yaml_frontmatter['name'] == 'test-skill'
        assert doc.yaml_frontmatter['description'] == 'A test skill for unit testing'

        # 验证 Markdown 正文不包含 frontmatter
        assert '---' not in doc.markdown_body
        assert '# Test Skill' in doc.markdown_body


class TestSkillDocumentSections:
    """测试章节解析功能"""

    @pytest.fixture
    def temp_skill(self, tmp_path):
        """创建包含多级标题的临时技能"""
        skill_dir = tmp_path / "multi-level-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""# Main Title

## Section 1

Content of section 1.

### Subsection 1.1

Nested content.

## Section 2

Content of section 2.
""")

        return skill_dir

    def test_sections_parsing(self, temp_skill):
        """测试章节解析"""
        doc = SkillDocument(temp_skill)

        # 验证章节被正确解析
        sections = doc.sections
        assert len(sections) >= 2

        # 验证章节包含标题和内容
        section_titles = [s.title for s in sections]
        assert any('Section 1' in title for title in section_titles)
        assert any('Section 2' in title for title in section_titles)

    def test_has_section(self, temp_skill):
        """测试 has_section 方法"""
        doc = SkillDocument(temp_skill)

        # 验证能检测到存在的章节
        assert doc.has_section('Section 1') == True
        assert doc.has_section('Section 2') == True

        # 验证检测不到不存在的章节
        assert doc.has_section('Non-existent Section') == False

    def test_get_section_content(self, temp_skill):
        """测试获取章节内容"""
        doc = SkillDocument(temp_skill)

        # 验证能获取章节内容
        content = doc.get_section_content('Section 1')
        assert content is not None
        assert 'Content of section 1' in content


class TestSkillDocumentCodeBlocks:
    """测试代码块解析功能"""

    @pytest.fixture
    def temp_skill(self, tmp_path):
        """创建包含多个代码块的临时技能"""
        skill_dir = tmp_path / "code-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""# Code Examples

## Python Example

```python
def greet(name):
    # This is a comment
    return f"Hello, {name}!"
```

## JavaScript Example

```javascript
function add(a, b) {
    return a + b;
}
```

## Unknown Language

```
Some code without language marker
```
""")

        return skill_dir

    def test_code_blocks_parsing(self, temp_skill):
        """测试代码块解析"""
        doc = SkillDocument(temp_skill)

        # 验证代码块被正确解析
        code_blocks = doc.code_blocks
        assert len(code_blocks) == 3

    def test_code_block_languages(self, temp_skill):
        """测试代码块语言识别"""
        doc = SkillDocument(temp_skill)

        languages = [block.language for block in doc.code_blocks]

        # 验证语言标记被正确识别
        assert 'python' in languages
        assert 'javascript' in languages
        assert 'unknown' in languages or '' in languages

    def test_code_block_content(self, temp_skill):
        """测试代码块内容"""
        doc = SkillDocument(temp_skill)

        python_blocks = [b for b in doc.code_blocks if b.language == 'python']
        assert len(python_blocks) >= 1

        # 验证代码内容被正确提取
        python_code = python_blocks[0].content
        assert 'def greet(name)' in python_code
        assert 'return f"Hello, {name}!"' in python_code

    def test_code_block_line_count(self, temp_skill):
        """测试代码块行数统计"""
        doc = SkillDocument(temp_skill)

        for block in doc.code_blocks:
            # 验证行数大于 0
            assert block.line_count > 0


class TestSkillDocumentLazyLoading:
    """测试懒加载机制"""

    @pytest.fixture
    def temp_skill(self, tmp_path):
        """创建测试技能"""
        skill_dir = tmp_path / "lazy-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("""# Lazy Test

## Section 1

Content here.

```python
print("test")
```
""")

        return skill_dir

    def test_lazy_loading_sections(self, temp_skill):
        """测试章节的懒加载"""
        doc = SkillDocument(temp_skill)

        # 第一次访问应该触发解析
        sections1 = doc.sections
        # 第二次访问应该返回缓存
        sections2 = doc.sections

        # 验证返回的是同一个对象（缓存）
        assert sections1 is sections2

    def test_lazy_loading_code_blocks(self, temp_skill):
        """测试代码块的懒加载"""
        doc = SkillDocument(temp_skill)

        # 第一次访问应该触发解析
        blocks1 = doc.code_blocks
        # 第二次访问应该返回缓存
        blocks2 = doc.code_blocks

        # 验证返回的是同一个对象（缓存）
        assert blocks1 is blocks2


class TestSkillDocumentMissingFiles:
    """测试处理缺失文件的情况"""

    def test_missing_metadata_json(self, tmp_path):
        """测试 metadata.json 缺失的情况"""
        skill_dir = tmp_path / "no-metadata-skill"
        skill_dir.mkdir()

        # 只创建 SKILL.md
        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("# Test Skill\n\nSome content.")

        doc = SkillDocument(skill_dir)

        # 验证即使没有 metadata.json 也能工作
        assert doc.metadata is None or doc.metadata == {}
        assert doc.raw_content is not None

    def test_no_yaml_frontmatter(self, tmp_path):
        """测试没有 YAML frontmatter 的情况"""
        skill_dir = tmp_path / "no-yaml-skill"
        skill_dir.mkdir()

        skill_md = skill_dir / "SKILL.md"
        skill_md.write_text("# Simple Skill\n\nNo frontmatter here.")

        doc = SkillDocument(skill_dir)

        # 验证没有 frontmatter 时返回 None
        assert doc.yaml_frontmatter is None or doc.yaml_frontmatter == {}
        # 验证 markdown_body 包含完整内容
        assert "# Simple Skill" in doc.markdown_body
