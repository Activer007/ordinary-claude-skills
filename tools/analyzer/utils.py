#!/usr/bin/env python3
"""
工具函数模块
提供 SKILL.md 解析、metadata.json 加载等基础功能
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import yaml


def load_skill_content(skill_path: Path) -> str:
    """
    加载 SKILL.md 文件内容

    Args:
        skill_path: 技能目录路径

    Returns:
        SKILL.md 的完整内容
    """
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        raise FileNotFoundError(f"SKILL.md not found in {skill_path}")

    with open(skill_file, 'r', encoding='utf-8') as f:
        return f.read()


def load_metadata(skill_path: Path) -> Optional[Dict]:
    """
    加载 metadata.json 文件

    Args:
        skill_path: 技能目录路径

    Returns:
        metadata 字典，如果文件不存在则返回 None
    """
    metadata_file = skill_path / "metadata.json"
    if not metadata_file.exists():
        return None

    try:
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None


def parse_yaml_frontmatter(content: str) -> Tuple[Optional[Dict], str]:
    """
    解析 YAML 前置元数据

    Args:
        content: 文件内容

    Returns:
        (元数据字典, 去除元数据后的内容)
    """
    # 匹配 YAML 前置元数据格式: ---\n...\n---
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)

    if not match:
        return None, content

    yaml_content = match.group(1)
    markdown_content = match.group(2)

    try:
        metadata = yaml.safe_load(yaml_content)
        return metadata, markdown_content
    except yaml.YAMLError:
        return None, content


def count_code_blocks(content: str) -> int:
    """
    统计代码块数量

    Args:
        content: Markdown 内容

    Returns:
        代码块数量
    """
    # 匹配 ``` 代码块
    pattern = r'```[\s\S]*?```'
    matches = re.findall(pattern, content)
    return len(matches)


def extract_code_blocks(content: str) -> List[str]:
    """
    提取所有代码块

    Args:
        content: Markdown 内容

    Returns:
        代码块列表
    """
    pattern = r'```[\s\S]*?```'
    return re.findall(pattern, content)


def count_sections(content: str) -> int:
    """
    统计 Markdown 章节数量

    Args:
        content: Markdown 内容

    Returns:
        章节数量（# 或 ## 标题）
    """
    # 匹配 Markdown 标题 (# 或 ##)
    pattern = r'^#{1,6}\s+.+$'
    matches = re.findall(pattern, content, re.MULTILINE)
    return len(matches)


def has_section(content: str, section_name: str) -> bool:
    """
    检查是否存在指定章节（支持模糊匹配和常见变体）

    Args:
        content: Markdown 内容
        section_name: 章节名称（不区分大小写）

    Returns:
        是否存在该章节
    """
    # 定义常见章节名称变体
    section_variants = {
        'When to Use': [
            'when to use',
            'when to use this skill',
            'usage scenario',
            'use cases',
            'when should',
            '使用场景',
            '适用场景'
        ],
        'Quick Start': [
            'quick start',
            'getting started',
            'quickstart',
            'get started',
            '快速开始',
            '入门'
        ],
        'Best Practice': [
            'best practice',
            'best practices',
            'recommendations',
            'guidelines',
            '最佳实践',
            '建议'
        ],
        'Example': [
            'example',
            'examples',
            'usage example',
            '示例',
            '用法示例'
        ],
    }

    # 获取要检查的变体列表
    patterns_to_check = [section_name.lower()]
    if section_name in section_variants:
        patterns_to_check.extend(section_variants[section_name])

    # 对每个变体进行匹配
    for variant in patterns_to_check:
        # 使用简单匹配，章节名称通常不包含特殊字符
        # 例如："When to Use" 可以匹配 "When to Use This Skill"
        # 注意：不能用 rf-string，因为 {1,6} 会被误解析
        pattern = r'^#{1,6}\s+.*' + re.escape(variant) + r'.*$'
        if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
            return True

    return False


def check_keywords(content: str, keywords: List[str]) -> bool:
    """
    检查内容中是否包含任一关键词

    Args:
        content: 文本内容
        keywords: 关键词列表

    Returns:
        是否包含任一关键词
    """
    content_lower = content.lower()
    return any(keyword.lower() in content_lower for keyword in keywords)


def count_keyword_occurrences(content: str, keywords: List[str]) -> int:
    """
    统计关键词出现次数

    Args:
        content: 文本内容
        keywords: 关键词列表

    Returns:
        关键词出现的总次数
    """
    content_lower = content.lower()
    total = 0
    for keyword in keywords:
        total += content_lower.count(keyword.lower())
    return total


def calculate_avg_line_length(content: str) -> float:
    """
    计算平均行长度

    Args:
        content: 文本内容

    Returns:
        平均行长度
    """
    lines = content.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]

    if not non_empty_lines:
        return 0.0

    total_length = sum(len(line) for line in non_empty_lines)
    return total_length / len(non_empty_lines)


def extract_use_cases(content: str) -> List[str]:
    """
    提取使用场景列表

    Args:
        content: Markdown 内容

    Returns:
        使用场景列表
    """
    # 查找 "When to Use" 章节
    # 仅从标题开始匹配章节内容
    pattern = r'^#{1,6}\s+.*(?:when to use|usage scenario).*?\n(.*?)(?=\n#{1,6}|\Z)'
    match = re.search(pattern, content, re.IGNORECASE | re.DOTALL | re.MULTILINE)

    if not match:
        return []

    section_content = match.group(1)

    # 提取列表项 (- 或 *)
    use_cases = re.findall(r'^[-*]\s+(.+)$', section_content, re.MULTILINE)
    return use_cases


def has_step_by_step(content: str) -> bool:
    """
    检查是否有 step-by-step 指导

    Args:
        content: 文本内容

    Returns:
        是否包含步骤指导
    """
    patterns = [
        r'\d+\.\s+',  # 数字列表 (1. 2. 3.)
        r'step\s+\d+',  # Step 1, Step 2
        r'first.*?then.*?finally',  # first...then...finally
    ]

    for pattern in patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return True

    return False


def load_config(config_path: Path) -> Dict:
    """
    加载配置文件

    Args:
        config_path: 配置文件路径

    Returns:
        配置字典
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)
