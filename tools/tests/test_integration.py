"""
端到端集成测试
测试完整的分析流程，确保各组件协同工作正常
"""
import pytest
import sys
import time
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer.skill_document import SkillDocument
from analyzer import utils


class TestEndToEndIntegration:
    """端到端集成测试"""

    @pytest.fixture
    def skills_dir(self):
        """获取 skills_all 目录"""
        return Path(__file__).parent.parent.parent / 'skills_all'

    @pytest.fixture
    def test_skill_paths(self, skills_dir):
        """获取用于测试的技能路径列表"""
        # 优先使用已知的高质量技能
        preferred_skills = [
            'api-design-principles',
            'nodejs-backend-patterns',
            'python-best-practices',
        ]

        test_skills = []
        for skill_name in preferred_skills:
            skill_path = skills_dir / skill_name
            if skill_path.exists():
                test_skills.append(skill_path)

        # 如果优先技能不存在，随机选择3个
        if len(test_skills) < 3:
            all_skills = [p for p in skills_dir.iterdir() if p.is_dir()]
            test_skills = all_skills[:3]

        return test_skills

    def test_full_analysis_with_skill_document(self, config, test_skill_paths):
        """测试使用 SkillDocument 的完整分析流程"""
        if not test_skill_paths:
            pytest.skip("没有可用的测试技能")

        skill_path = test_skill_paths[0]
        analyzer = SkillAnalyzer(skill_path, config)
        result = analyzer.analyze()

        # 验证结果结构完整
        assert 'skill_name' in result
        assert 'skill_path' in result
        assert 'total_score' in result
        assert 'grade' in result
        assert 'scores' in result

        # 验证没有错误
        assert 'error' not in result or result.get('error') is None

        # 验证总分在有效范围
        assert 0 <= result['total_score'] <= 100

        # 验证评分维度完整
        assert 'content' in result['scores']
        assert 'technical' in result['scores']
        assert 'maintenance' in result['scores']
        assert 'ux' in result['scores']

        # 验证每个维度都有 total 和 details
        for dimension in ['content', 'technical', 'maintenance', 'ux']:
            assert 'total' in result['scores'][dimension]
            assert 'details' in result['scores'][dimension]

        # 验证等级正确
        assert result['grade'] in ['S', 'A', 'B', 'C', 'D', 'ERROR']

        # 如果没有错误，等级不应该是 ERROR
        if 'error' not in result:
            assert result['grade'] != 'ERROR'

        print(f"\n✓ 完整分析测试通过: {skill_path.name} - {result['total_score']}分 ({result['grade']}级)")

    def test_skill_document_caching(self, test_skill_paths):
        """测试 SkillDocument 的缓存机制"""
        if not test_skill_paths:
            pytest.skip("没有可用的测试技能")

        skill_path = test_skill_paths[0]
        doc = SkillDocument(skill_path)

        # 首次访问 sections - 触发解析
        start = time.time()
        sections_first = doc.sections
        first_access_time = time.time() - start

        # 第二次访问 sections - 使用缓存
        start = time.time()
        sections_second = doc.sections
        cached_access_time = time.time() - start

        # 验证缓存有效：第二次访问应该显著更快
        assert cached_access_time < first_access_time or cached_access_time < 0.001

        # 验证返回的是同一个对象（缓存）
        assert sections_first is sections_second

        print(f"\n✓ 缓存测试通过:")
        print(f"  首次访问: {first_access_time*1000:.2f}ms")
        print(f"  缓存访问: {cached_access_time*1000:.2f}ms")

    def test_skill_document_lazy_loading(self, test_skill_paths):
        """测试 SkillDocument 的懒加载机制"""
        if not test_skill_paths:
            pytest.skip("没有可用的测试技能")

        skill_path = test_skill_paths[0]

        # 测试初始化速度（不应解析内容）
        start = time.time()
        doc = SkillDocument(skill_path)
        init_time = time.time() - start

        # 初始化应该很快（懒加载）
        assert init_time < 0.1  # 小于100ms

        # 验证私有属性尚未初始化（懒加载）
        assert doc._sections is None
        assert doc._code_blocks is None

        # 访问属性后应该初始化
        _ = doc.sections
        assert doc._sections is not None

        _ = doc.code_blocks
        assert doc._code_blocks is not None

        print(f"\n✓ 懒加载测试通过: 初始化时间 {init_time*1000:.2f}ms")

    def test_batch_analysis_consistency(self, config, test_skill_paths):
        """测试批量分析的一致性"""
        if len(test_skill_paths) < 3:
            pytest.skip("测试技能数量不足（需要至少3个）")

        results = []

        # 批量分析
        for skill_path in test_skill_paths[:3]:
            analyzer = SkillAnalyzer(skill_path, config)
            result = analyzer.analyze()
            results.append(result)

        # 验证所有技能都得到了有效评分
        for i, result in enumerate(results):
            skill_name = test_skill_paths[i].name

            # 应该没有错误或有有效的错误处理
            if 'error' in result and result['error']:
                print(f"\n⚠ {skill_name} 分析出错: {result['error']}")
                # 出错时应该有默认值
                assert result['total_score'] == 0
                assert result['grade'] == 'ERROR'
            else:
                # 正常情况下分数应该在有效范围
                assert 0 <= result['total_score'] <= 100
                assert result['grade'] in ['S', 'A', 'B', 'C', 'D']

        # 验证评分的一致性（相同技能多次分析应该得到相同结果）
        if results and 'error' not in results[0]:
            skill_path = test_skill_paths[0]
            analyzer = SkillAnalyzer(skill_path, config)
            result_repeat = analyzer.analyze()

            assert result_repeat['total_score'] == results[0]['total_score']
            assert result_repeat['grade'] == results[0]['grade']

        print(f"\n✓ 批量分析一致性测试通过:")
        for i, result in enumerate(results):
            skill_name = test_skill_paths[i].name
            if 'error' not in result or not result['error']:
                print(f"  {skill_name}: {result['total_score']}分 ({result['grade']}级)")
            else:
                print(f"  {skill_name}: ERROR - {result['error']}")

    def test_analysis_performance(self, config, test_skill_paths):
        """测试单个技能分析性能"""
        if not test_skill_paths:
            pytest.skip("没有可用的测试技能")

        skill_path = test_skill_paths[0]

        # 测试分析速度
        start = time.time()
        analyzer = SkillAnalyzer(skill_path, config)
        result = analyzer.analyze()
        duration = time.time() - start

        # 单个技能分析应该在合理时间内完成（<2秒）
        assert duration < 2.0

        # 第二次分析应该更快（使用缓存）
        start = time.time()
        result2 = analyzer.analyze()
        duration2 = time.time() - start

        # 虽然SkillAnalyzer每次都创建新的SkillDocument，
        # 但文件系统缓存应该使第二次更快
        # 这里不做严格断言，只是记录
        print(f"\n✓ 性能测试:")
        print(f"  首次分析: {duration*1000:.2f}ms")
        print(f"  二次分析: {duration2*1000:.2f}ms")

    def test_recommendations_generation(self, config, tmp_path):
        """测试改进建议生成"""
        # 创建一个低质量的测试技能
        temp_skill = tmp_path / "low-quality-skill"
        temp_skill.mkdir()

        skill_md = temp_skill / "SKILL.md"
        skill_md.write_text("""
# Low Quality Skill

This is a minimal skill without proper structure.

Some random text.
""")

        analyzer = SkillAnalyzer(temp_skill, config)
        result = analyzer.analyze()

        # 验证生成了改进建议
        assert 'recommendations' in result
        assert isinstance(result['recommendations'], list)

        # 低质量技能应该有多个改进建议
        assert len(result['recommendations']) > 0

        # 验证建议内容合理
        recommendations_text = ' '.join(result['recommendations'])

        # 应该建议添加 When to Use 章节（因为缺少）
        assert any('When to Use' in rec or '使用场景' in rec for rec in result['recommendations'])

        print(f"\n✓ 改进建议生成测试通过: 生成了 {len(result['recommendations'])} 条建议")
        for rec in result['recommendations'][:5]:  # 只打印前5条
            print(f"  - {rec}")

    def test_error_handling(self, config, tmp_path):
        """测试错误处理"""
        # 测试1: 不存在的技能目录
        nonexistent_path = tmp_path / "nonexistent-skill"
        analyzer = SkillAnalyzer(nonexistent_path, config)
        result = analyzer.analyze()

        # 应该返回错误信息而不是崩溃
        assert 'error' in result
        assert result['total_score'] == 0
        assert result['grade'] == 'ERROR'

        # 测试2: 空的技能目录
        empty_skill = tmp_path / "empty-skill"
        empty_skill.mkdir()

        analyzer = SkillAnalyzer(empty_skill, config)
        result = analyzer.analyze()

        # 应该处理空目录情况
        assert 'error' in result or result['total_score'] == 0

        print(f"\n✓ 错误处理测试通过")

    def test_multiple_scorers_integration(self, config, tmp_path):
        """测试多个评分器的集成"""
        # 创建一个结构完整的测试技能
        temp_skill = tmp_path / "complete-skill"
        temp_skill.mkdir()

        skill_md = temp_skill / "SKILL.md"
        skill_md.write_text("""
---
name: complete-skill
description: A complete skill for testing
---

# Complete Skill

## When to Use This Skill

- Use case 1: Building REST APIs
- Use case 2: Creating microservices
- Use case 3: Designing scalable systems

## Best Practices

Follow these best practices:
- Input validation
- Error handling
- Security considerations

## Examples

```python
def validate_input(data):
    if not data:
        raise ValueError("Invalid input")
    return data

try:
    result = validate_input(user_data)
except ValueError as e:
    logging.error(f"Validation error: {e}")
```

```javascript
function handleError(error) {
    console.error(error);
    return { success: false, error: error.message };
}
```

## Quick Start

Get started in 5 minutes.
""")

        # 创建 metadata.json
        metadata_file = temp_skill / "metadata.json"
        metadata_file.write_text("""{
    "id": "complete-skill",
    "name": "Complete Skill",
    "author": "test-author",
    "description": "A complete skill for testing",
    "updatedAt": 1704067200
}""")

        analyzer = SkillAnalyzer(temp_skill, config)
        result = analyzer.analyze()

        # 验证所有评分器都正常工作
        assert 'error' not in result or not result['error']

        # 验证内容质量评分
        content = result['scores']['content']
        assert content['details']['has_when_to_use'] == True
        assert content['details']['use_cases_count'] >= 3
        assert content['details']['has_best_practices'] == True

        # 验证技术实现评分
        technical = result['scores']['technical']
        assert technical['details']['code_blocks_count'] >= 2
        assert technical['details']['has_security_keywords'] == True
        assert technical['details']['has_error_handling'] == True

        # 验证用户体验评分
        ux = result['scores']['ux']
        assert ux['details']['has_quick_start'] == True
        assert ux['details']['sections_count'] >= 4

        # 验证总分合理
        assert result['total_score'] > 40  # 应该是合格质量

        print(f"\n✓ 多评分器集成测试通过:")
        print(f"  内容质量: {content['total']}/50")
        print(f"  技术实现: {technical['total']}/30")
        print(f"  维护性: {result['scores']['maintenance']['total']}/10")
        print(f"  用户体验: {ux['total']}/10")
        print(f"  总分: {result['total_score']}/100 ({result['grade']}级)")
