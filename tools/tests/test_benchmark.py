#!/usr/bin/env python3
"""
性能基准测试 (Benchmark Tests)

用于监控性能改进效果，防止性能回退。

运行方式：
    # 运行所有基准测试（包含内存测试）
    pytest tools/tests/test_benchmark.py

    # 仅运行性能基准测试（跳过内存测试）
    pytest tools/tests/test_benchmark.py --benchmark-only

    # 保存基线
    pytest tools/tests/test_benchmark.py --benchmark-save=baseline

    # 对比性能变化
    pytest tools/tests/test_benchmark.py --benchmark-compare=baseline

    # 生成性能报告
    pytest tools/tests/test_benchmark.py --benchmark-autosave

Created: 2026-01-13
"""

import pytest
import time
import tracemalloc
import sys
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.skill_analyzer import SkillAnalyzer
from analyzer.skill_document import SkillDocument


class TestSingleSkillPerformance:
    """单个技能分析性能测试"""

    @pytest.fixture
    def skills_dir(self):
        """获取 skills_all 目录"""
        return Path(__file__).parent.parent.parent / 'skills_all'

    def test_single_skill_analysis_speed(self, benchmark, config, skills_dir):
        """
        测试单个技能分析速度

        期望：单个技能分析 < 2 秒（合理预期，考虑文件 I/O）
        """
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        def analyze():
            analyzer = SkillAnalyzer(skill_path, config)
            return analyzer.analyze()

        result = benchmark(analyze)

        # 验证分析成功
        assert 'error' not in result
        assert result['total_score'] > 0

        # 性能期望：单个技能分析 < 2 秒
        assert benchmark.stats['mean'] < 2.0, \
            f"分析速度过慢: {benchmark.stats['mean']:.3f}s (期望 < 2.0s)"

    def test_skill_document_initialization_speed(self, benchmark, skills_dir):
        """
        测试 SkillDocument 初始化速度（懒加载）

        期望：初始化 < 100ms（不应解析内容）
        """
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        def init_document():
            return SkillDocument(skill_path)

        doc = benchmark(init_document)

        # 验证初始化成功
        assert doc is not None
        assert doc.path == skill_path

        # 性能期望：初始化很快（懒加载）
        assert benchmark.stats['mean'] < 0.1, \
            f"初始化过慢: {benchmark.stats['mean']:.3f}s (期望 < 0.1s)"


class TestBatchAnalysisPerformance:
    """批量分析性能测试"""

    @pytest.fixture
    def skills_dir(self):
        """获取 skills_all 目录"""
        return Path(__file__).parent.parent.parent / 'skills_all'

    def test_batch_analysis_throughput(self, benchmark, config, skills_dir):
        """
        测试批量分析吞吐量

        期望：10 个技能分析 < 20 秒（平均 2s/个）
        """
        if not skills_dir.exists():
            pytest.skip("skills_all 目录不存在")

        # 选择前 10 个技能
        skills = sorted([d for d in skills_dir.iterdir() if d.is_dir()])[:10]

        if len(skills) < 5:
            pytest.skip("技能数量不足")

        def batch_analyze():
            results = []
            for skill in skills:
                try:
                    analyzer = SkillAnalyzer(skill, config)
                    result = analyzer.analyze()
                    results.append(result)
                except Exception as e:
                    # 跳过有问题的技能
                    pass
            return results

        results = benchmark(batch_analyze)

        # 验证至少成功分析了一些技能
        assert len(results) > 0

        # 性能期望：10 个技能 < 20 秒
        assert benchmark.stats['mean'] < 20.0, \
            f"批量分析过慢: {benchmark.stats['mean']:.3f}s (期望 < 20.0s)"


class TestLazyLoadingPerformance:
    """懒加载性能测试"""

    @pytest.fixture
    def skills_dir(self):
        """获取 skills_all 目录"""
        return Path(__file__).parent.parent.parent / 'skills_all'

    def test_lazy_loading_effectiveness(self, skills_dir):
        """
        测试懒加载的有效性

        验证：
        1. 初始化很快（不解析内容）
        2. 首次访问触发解析
        3. 缓存访问非常快
        """
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        # 测试 1: 初始化应该很快
        start = time.time()
        doc = SkillDocument(skill_path)
        init_time = time.time() - start

        assert init_time < 0.1, \
            f"初始化过慢: {init_time:.3f}s (期望 < 0.1s)"

        # 测试 2: 首次访问触发解析
        start = time.time()
        sections = doc.sections
        first_access = time.time() - start

        assert len(sections) > 0, "应该解析到章节"

        # 测试 3: 缓存访问应该非常快
        start = time.time()
        sections_cached = doc.sections
        cached_access = time.time() - start

        # 验证缓存访问快很多（至少 10 倍）
        assert cached_access < first_access / 10, \
            f"缓存未生效: 首次 {first_access:.4f}s vs 缓存 {cached_access:.4f}s"

        # 缓存访问应该 < 1ms
        assert cached_access < 0.001, \
            f"缓存访问过慢: {cached_access:.6f}s (期望 < 0.001s)"

    def test_code_blocks_lazy_loading(self, skills_dir):
        """
        测试代码块懒加载

        验证缓存对代码块解析的效果
        """
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        doc = SkillDocument(skill_path)

        # 首次访问
        start = time.time()
        code_blocks_1 = doc.code_blocks
        first_access = time.time() - start

        # 缓存访问
        start = time.time()
        code_blocks_2 = doc.code_blocks
        cached_access = time.time() - start

        # 验证返回相同对象（缓存生效）
        assert code_blocks_1 is code_blocks_2, "应该返回缓存的对象"

        # 缓存访问应该非常快
        assert cached_access < 0.001, \
            f"缓存访问过慢: {cached_access:.6f}s (期望 < 0.001s)"


class TestMemoryUsage:
    """内存使用测试"""

    @pytest.fixture
    def skills_dir(self):
        """获取 skills_all 目录"""
        return Path(__file__).parent.parent.parent / 'skills_all'

    def test_memory_usage_single_skill(self, config, skills_dir):
        """
        测试单个技能分析的内存使用

        期望：峰值内存 < 50MB
        """
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        tracemalloc.start()

        # 分析单个技能
        analyzer = SkillAnalyzer(skill_path, config)
        result = analyzer.analyze()

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 验证分析成功
        assert 'error' not in result

        # 内存期望：峰值 < 50MB
        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 50, \
            f"内存使用过高: {peak_mb:.2f}MB (期望 < 50MB)"

    def test_memory_usage_batch_analysis(self, config, skills_dir):
        """
        测试批量分析的内存使用

        期望：分析 10 个技能，峰值内存 < 100MB
        """
        if not skills_dir.exists():
            pytest.skip("skills_all 目录不存在")

        # 选择前 10 个技能
        skills = sorted([d for d in skills_dir.iterdir() if d.is_dir()])[:10]

        if len(skills) < 5:
            pytest.skip("技能数量不足")

        tracemalloc.start()

        # 批量分析
        results = []
        for skill in skills:
            try:
                analyzer = SkillAnalyzer(skill, config)
                result = analyzer.analyze()
                results.append(result)
            except Exception:
                pass

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 验证至少成功分析了一些技能
        assert len(results) > 0

        # 内存期望：峰值 < 100MB
        peak_mb = peak / (1024 * 1024)
        assert peak_mb < 100, \
            f"批量分析内存过高: {peak_mb:.2f}MB (期望 < 100MB)"

    def test_no_memory_leak_on_repeated_analysis(self, config, skills_dir):
        """
        测试重复分析是否存在内存泄漏

        验证：重复分析同一技能，内存增长应该很小
        """
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        tracemalloc.start()

        # 第一次分析
        analyzer = SkillAnalyzer(skill_path, config)
        analyzer.analyze()

        # 获取第一次分析后的内存
        current_1, _ = tracemalloc.get_traced_memory()

        # 重复分析 5 次
        for _ in range(5):
            analyzer = SkillAnalyzer(skill_path, config)
            analyzer.analyze()

        # 获取重复分析后的内存
        current_2, _ = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # 内存增长应该很小（< 5MB）
        memory_growth = (current_2 - current_1) / (1024 * 1024)
        assert memory_growth < 5, \
            f"疑似内存泄漏: 增长 {memory_growth:.2f}MB (期望 < 5MB)"


class TestPerformanceRegression:
    """性能回归测试"""

    @pytest.fixture
    def skills_dir(self):
        """获取 skills_all 目录"""
        return Path(__file__).parent.parent.parent / 'skills_all'

    def test_no_performance_regression(self, benchmark, config, skills_dir):
        """
        性能回归检测

        运行基准测试以检测性能回退。
        使用 --benchmark-compare 参数对比历史基线。
        """
        skill_path = skills_dir / 'api-design-principles'

        if not skill_path.exists():
            pytest.skip("api-design-principles 技能不存在")

        def analyze():
            analyzer = SkillAnalyzer(skill_path, config)
            return analyzer.analyze()

        result = benchmark(analyze)

        # 验证分析成功
        assert 'error' not in result
        assert result['total_score'] > 0


if __name__ == '__main__':
    pytest.main([__file__, '--benchmark-only', '-v'])
