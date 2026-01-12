"""
测试平滑评分函数
"""
import pytest
import sys
import math
from pathlib import Path

# 添加父目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from analyzer.scoring_utils import smooth_score


class TestSmoothScore:
    """测试平滑评分函数"""

    def test_zero_value(self):
        """测试输入为 0 的情况"""
        assert smooth_score(0, max_value=10, max_score=10) == 0

    def test_max_value(self):
        """测试输入达到或超过 max_value 的情况"""
        assert smooth_score(10, max_value=10, max_score=10) == 10
        assert smooth_score(15, max_value=10, max_score=10) == 10

    def test_negative_value(self):
        """测试负值输入"""
        assert smooth_score(-5, max_value=10, max_score=10) == 0

    def test_smooth_curve(self):
        """测试评分曲线的平滑性"""
        # 对数平滑应该让大多数值有区分度
        scores = [smooth_score(i, max_value=8, max_score=10) for i in range(9)]

        # 验证递增性（允许相邻值得分相同，但不能递减）
        for i in range(len(scores) - 1):
            assert scores[i] <= scores[i + 1], f"Score at {i} should be <= score at {i+1}"

        # 验证至少有 5 个不同的分数（比阶梯式评分更好）
        unique_scores = set(scores[1:])  # 排除 0
        assert len(unique_scores) >= 5, f"应该有至少 5 个不同的分数，实际有 {len(unique_scores)}"

    def test_realistic_code_blocks_scoring(self):
        """测试实际的代码块评分场景"""
        # 代码块数量从 1 到 8 的评分
        scores = {
            1: smooth_score(1, max_value=8, max_score=10),
            2: smooth_score(2, max_value=8, max_score=10),
            3: smooth_score(3, max_value=8, max_score=10),
            4: smooth_score(4, max_value=8, max_score=10),
            5: smooth_score(5, max_value=8, max_score=10),
            6: smooth_score(6, max_value=8, max_score=10),
            7: smooth_score(7, max_value=8, max_score=10),
            8: smooth_score(8, max_value=8, max_score=10),
        }

        # 验证区分度：应该至少有 5 个不同的分数（比阶梯式的 4 个更好）
        unique_scores = set(scores.values())
        assert len(unique_scores) >= 5, f"应该有至少 5 个不同的分数，实际有 {len(unique_scores)}"

        # 验证 8 个代码块得满分
        assert scores[8] == 10

        # 验证 1 个代码块得分 > 0
        assert scores[1] > 0

        # 验证递增性
        assert scores[1] < scores[2] < scores[3] <= scores[4] <= scores[8]

    def test_different_max_scores(self):
        """测试不同的 max_score 参数"""
        # 使用不同的 max_score，比例应该保持一致
        score_10 = smooth_score(5, max_value=10, max_score=10)
        score_20 = smooth_score(5, max_value=10, max_score=20)

        # score_20 应该是 score_10 的 2 倍（大约）
        assert abs(score_20 - score_10 * 2) <= 1  # 允许 1 分的误差

    def test_sections_scoring(self):
        """测试章节数量评分"""
        # 章节数量从 1 到 10 的评分
        scores = [smooth_score(i, max_value=10, max_score=6) for i in range(1, 11)]

        # 验证递增性（允许相邻值相同）
        for i in range(len(scores) - 1):
            assert scores[i] <= scores[i + 1]

        # 验证最大值
        assert scores[-1] == 6

    def test_use_cases_scoring(self):
        """测试使用场景数量评分"""
        # 使用场景从 1 到 5 的评分
        scores = {
            1: smooth_score(1, max_value=5, max_score=5),
            2: smooth_score(2, max_value=5, max_score=5),
            3: smooth_score(3, max_value=5, max_score=5),
            4: smooth_score(4, max_value=5, max_score=5),
            5: smooth_score(5, max_value=5, max_score=5),
        }

        # 验证有良好的区分度（至少 4 个不同分数，比阶梯式更好）
        unique_scores = set(scores.values())
        assert len(unique_scores) >= 4

        # 验证 5 个使用场景得满分
        assert scores[5] == 5

        # 验证递增性
        assert scores[1] <= scores[2] <= scores[3] <= scores[4] <= scores[5]


class TestSmoothScoreEdgeCases:
    """测试平滑评分函数的边界情况"""

    def test_very_large_value(self):
        """测试非常大的输入值"""
        assert smooth_score(1000, max_value=10, max_score=10) == 10

    def test_max_value_is_zero(self):
        """测试 max_value 为 0 的情况"""
        # 应该避免除以零错误
        result = smooth_score(5, max_value=0, max_score=10)
        # 当 max_value 为 0 时，任何正值都应该得满分
        assert result == 10

    def test_fractional_values(self):
        """测试小数输入"""
        score1 = smooth_score(2.5, max_value=5, max_score=10)
        score2 = smooth_score(2, max_value=5, max_score=10)
        score3 = smooth_score(3, max_value=5, max_score=10)

        # 2.5 的分数应该介于 2 和 3 之间
        assert score2 < score1 < score3


class TestSmoothScoreComparison:
    """对比旧的阶梯式评分和新的平滑评分"""

    def test_old_vs_new_scoring(self):
        """对比旧的阶梯式评分和新的平滑评分"""
        # 旧方式：代码块评分（阶梯式）
        def old_score(code_blocks):
            if code_blocks >= 5:
                return 10
            elif code_blocks >= 3:
                return 7
            elif code_blocks >= 2:
                return 5
            elif code_blocks >= 1:
                return 3
            return 0

        # 新方式：平滑评分
        def new_score(code_blocks):
            return smooth_score(code_blocks, max_value=8, max_score=10)

        # 旧方式：3 个和 4 个代码块得分相同
        assert old_score(3) == old_score(4) == 7

        # 新方式：3 个和 4 个代码块得分不同
        assert new_score(3) < new_score(4)

        print("\n旧方式 vs 新方式对比：")
        print("代码块数 | 旧评分 | 新评分")
        print("---------|-------|-------")
        for i in range(1, 9):
            print(f"   {i}     |  {old_score(i):>2}   |  {new_score(i):>2}")
