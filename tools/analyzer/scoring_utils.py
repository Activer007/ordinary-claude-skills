#!/usr/bin/env python3
"""
评分工具函数

提供平滑评分曲线等通用功能
"""

import math
from typing import Union


def smooth_score(value: Union[int, float], max_value: Union[int, float], max_score: int) -> int:
    """
    平滑评分函数

    使用对数曲线，让更多的值有区分度，避免阶梯式评分的问题。

    原理：
    - 阶梯式评分：score = [0, 3, 5, 7, 7, 10, 10, ...]（4和3、5和6得分相同）
    - 平滑评分：score = [0, 3, 5, 6, 7, 8, 9, 10, ...]（每个值都有区分度）

    Args:
        value: 输入值（例如代码块数量）
        max_value: 达到满分所需的最大值
        max_score: 最高分数

    Returns:
        平滑后的得分（0 到 max_score 之间的整数）

    Examples:
        >>> smooth_score(3, max_value=8, max_score=10)
        6
        >>> smooth_score(5, max_value=8, max_score=10)
        8
        >>> smooth_score(8, max_value=8, max_score=10)
        10
    """
    # 处理边界情况
    if value <= 0:
        return 0

    if max_value <= 0:
        # 避免除以零，任何正值都返回满分
        return max_score

    if value >= max_value:
        return max_score

    # 对数平滑公式：
    # ratio = log(1 + value) / log(1 + max_value)
    # score = ratio * max_score
    #
    # 使用 log(1 + x) 而不是 log(x) 的原因：
    # 1. 避免 log(0) 未定义的问题
    # 2. 让 value=1 时也能得到合理的分数
    ratio = math.log(1 + value) / math.log(1 + max_value)
    score = ratio * max_score

    # 四舍五入并确保在有效范围内
    return int(round(score))


def linear_score(value: Union[int, float], max_value: Union[int, float], max_score: int) -> int:
    """
    线性评分函数（备用）

    Args:
        value: 输入值
        max_value: 达到满分所需的最大值
        max_score: 最高分数

    Returns:
        线性分数（0 到 max_score 之间的整数）
    """
    if value <= 0:
        return 0

    if max_value <= 0:
        return max_score

    if value >= max_value:
        return max_score

    ratio = value / max_value
    score = ratio * max_score

    return int(round(score))
