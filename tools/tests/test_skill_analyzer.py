"""
测试 skill_analyzer.py（集成测试）
"""
import pytest
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer import utils


class TestSkillAnalyzerIntegration:
    """集成测试：使用真实技能文件"""

    @pytest.fixture
    def skills_dir(self):
        """获取 skills_all 目录"""
        return Path(__file__).parent.parent.parent / 'skills_all'

    def test_analyze_api_design_principles(self, skills_dir, config):
        """测试分析 api-design-principles（高质量技能）"""
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        analyzer = SkillAnalyzer(skill_path, config)
        result = analyzer.analyze()

        # 验证分析成功
        assert 'error' not in result

        # 验证检测到了 When to Use 章节
        assert result['scores']['content']['details']['has_when_to_use'] == True

        # 验证总分在预期范围（修复后应该 > 80）
        assert result['total_score'] >= 70  # 至少 B 级

        # 验证等级
        assert result['grade'] in ['S', 'A', 'B']

        print(f"\n✓ api-design-principles: {result['total_score']}分 ({result['grade']}级)")

    def test_analyze_nodejs_backend_patterns(self, skills_dir, config):
        """测试分析 nodejs-backend-patterns（高质量技能）"""
        skill_path = skills_dir / 'nodejs-backend-patterns'

        if not skill_path.exists():
            pytest.skip("nodejs-backend-patterns 技能不存在")

        analyzer = SkillAnalyzer(skill_path, config)
        result = analyzer.analyze()

        # 验证分析成功
        assert 'error' not in result

        # 验证检测到了 When to Use 章节
        assert result['scores']['content']['details']['has_when_to_use'] == True

        # 验证总分
        assert result['total_score'] >= 75

        print(f"\n✓ nodejs-backend-patterns: {result['total_score']}分 ({result['grade']}级)")

    def test_handle_missing_metadata(self, config, tmp_path):
        """测试处理缺失 metadata.json 的情况"""
        # 创建临时技能目录
        temp_skill = tmp_path / "test-skill"
        temp_skill.mkdir()

        # 只创建 SKILL.md，不创建 metadata.json
        skill_md = temp_skill / "SKILL.md"
        skill_md.write_text("""
# Test Skill

## When to Use This Skill

- Test case 1
- Test case 2

```python
print("test")
```
""")

        analyzer = SkillAnalyzer(temp_skill, config)
        result = analyzer.analyze()

        # 验证分析成功（即使缺少 metadata）
        assert 'error' not in result

        # 验证基本评分正常
        assert result['total_score'] > 0

        print(f"\n✓ 临时测试技能（无 metadata）: {result['total_score']}分")
