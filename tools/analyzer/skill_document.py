#!/usr/bin/env python3
"""
SkillDocument 预处理层
提供技能文档的结构化表示和一次解析、多处复用的能力
"""

import json
import re
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from dataclasses import dataclass
import yaml


@dataclass
class Section:
    """章节的结构化表示"""
    title: str          # 章节标题
    level: int          # 标题级别 (1-6)
    content: str        # 章节内容
    start_line: int     # 起始行号
    end_line: int       # 结束行号

    def matches(self, name: str) -> bool:
        """
        检查章节名称是否匹配（不区分大小写，使用词边界）

        使用词边界匹配避免部分单词误匹配：
        - "When to Use" 匹配 "When to Use This Skill" ✓
        - "Use" 不匹配 "Reuse Patterns" ✗

        Args:
            name: 要匹配的名称

        Returns:
            是否匹配
        """
        # 过滤空字符串和纯空白字符串
        if not name or not name.strip():
            return False

        title_lower = self.title.lower()
        name_lower = name.lower()

        # 使用词边界避免部分单词匹配
        # \b 确保匹配的是完整单词，而不是单词的一部分
        # 允许末尾有可选的 's' 以支持单复数匹配 (e.g. "Example" 匹配 "Examples")
        pattern = r'\b' + re.escape(name_lower) + r's?\b'
        return bool(re.search(pattern, title_lower))


@dataclass
class CodeBlock:
    """代码块的结构化表示"""
    language: str          # 代码语言（python, typescript, bash 等）
    content: str           # 代码内容
    line_count: int        # 行数
    has_comments: bool     # 是否有注释
    is_complete: bool      # 是否看起来完整（有函数定义、类定义等）
    has_error_handling: bool  # 是否包含错误处理


class SkillDocument:
    """
    技能文档的结构化表示

    提供一次解析、多处复用的能力，避免重复计算
    """

    def __init__(self, skill_path: Path):
        """
        初始化 SkillDocument

        Args:
            skill_path: 技能目录路径
        """
        self.path = Path(skill_path)
        self.raw_content = self._load_content()
        self.metadata = self._load_metadata()
        self.yaml_frontmatter, self.markdown_body = self._parse_frontmatter()

        # 懒加载缓存
        self._sections = None
        self._code_blocks = None

    def _load_content(self) -> str:
        """
        加载 SKILL.md 文件内容

        Returns:
            SKILL.md 的完整内容

        Raises:
            FileNotFoundError: 如果 SKILL.md 不存在
        """
        skill_file = self.path / "SKILL.md"
        if not skill_file.exists():
            raise FileNotFoundError(f"SKILL.md not found in {self.path}")

        with open(skill_file, 'r', encoding='utf-8') as f:
            return f.read()

    def _load_metadata(self) -> Optional[Dict]:
        """
        加载 metadata.json 文件

        Returns:
            metadata 字典，如果文件不存在则返回 None
        """
        metadata_file = self.path / "metadata.json"
        if not metadata_file.exists():
            return None

        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return None

    def _parse_frontmatter(self) -> Tuple[Optional[Dict], str]:
        """
        解析 YAML 前置元数据

        Returns:
            (元数据字典, 去除元数据后的内容)
        """
        # 匹配 YAML 前置元数据格式: ---\n...\n---
        pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
        match = re.match(pattern, self.raw_content, re.DOTALL)

        if not match:
            return None, self.raw_content

        yaml_content = match.group(1)
        markdown_content = match.group(2)

        try:
            metadata = yaml.safe_load(yaml_content)
            return metadata, markdown_content
        except yaml.YAMLError:
            return None, self.raw_content

    @property
    def sections(self) -> List[Section]:
        """
        解析所有章节（带层级）

        Returns:
            章节列表
        """
        if self._sections is None:
            self._sections = self._parse_sections()
        return self._sections

    def _parse_sections(self) -> List[Section]:
        """
        解析 Markdown 章节

        Returns:
            Section 对象列表
        """
        sections = []
        lines = self.markdown_body.split('\n')

        # 匹配 Markdown 标题 (# 或 ##, ###, 等)
        heading_pattern = r'^(#{1,6})\s+(.+)$'

        current_section = None
        content_lines = []
        start_line = 0

        for i, line in enumerate(lines):
            match = re.match(heading_pattern, line)

            if match:
                # 保存前一个章节
                if current_section is not None:
                    current_section.content = '\n'.join(content_lines)
                    current_section.end_line = i - 1
                    sections.append(current_section)

                # 开始新章节
                level = len(match.group(1))
                title = match.group(2).strip()

                current_section = Section(
                    title=title,
                    level=level,
                    content='',
                    start_line=i,
                    end_line=-1
                )
                content_lines = []
                start_line = i + 1
            else:
                # 累积章节内容
                if current_section is not None:
                    content_lines.append(line)

        # 保存最后一个章节
        if current_section is not None:
            current_section.content = '\n'.join(content_lines)
            current_section.end_line = len(lines) - 1
            sections.append(current_section)

        return sections

    @property
    def code_blocks(self) -> List[CodeBlock]:
        """
        解析所有代码块（带语言标记）

        Returns:
            CodeBlock 对象列表
        """
        if self._code_blocks is None:
            self._code_blocks = self._parse_code_blocks()
        return self._code_blocks

    def _parse_code_blocks(self) -> List[CodeBlock]:
        """
        深度分析代码块

        Returns:
            CodeBlock 对象列表
        """
        # 兼容语言标识符后的空格
        pattern = r'```(\w*)[ \t]*\n(.*?)```'
        blocks = []

        for match in re.finditer(pattern, self.markdown_body, re.DOTALL):
            language = match.group(1) or 'unknown'
            code = match.group(2)

            blocks.append(CodeBlock(
                language=language,
                content=code,
                line_count=len(code.strip().split('\n')),
                has_comments=self._detect_comments(code, language),
                is_complete=self._detect_completeness(code, language),
                has_error_handling=self._detect_error_handling(code, language),
            ))

        return blocks

    def _detect_comments(self, code: str, language: str) -> bool:
        """
        检测代码中是否有注释

        Args:
            code: 代码内容
            language: 编程语言

        Returns:
            是否包含注释
        """
        comment_patterns = {
            'python': r'#',
            'javascript': r'//',
            'typescript': r'//',
            'java': r'//',
            'bash': r'#',
            'shell': r'#',
        }

        pattern = comment_patterns.get(language.lower(), r'#|//')
        return bool(re.search(pattern, code))

    def _detect_completeness(self, code: str, language: str) -> bool:
        """
        检测代码是否看起来完整（有函数/类定义）

        Args:
            code: 代码内容
            language: 编程语言

        Returns:
            是否完整
        """
        completeness_patterns = {
            'python': r'(def |class |async def )',
            'javascript': r'(function |class |const .* = |let .* = )',
            'typescript': r'(function |class |const .* = |interface |type )',
            'java': r'(public |private |protected |class |interface )',
        }

        pattern = completeness_patterns.get(language.lower(), r'(function|class|def)')
        return bool(re.search(pattern, code))

    def _detect_error_handling(self, code: str, language: str) -> bool:
        """
        检测代码是否包含错误处理

        Args:
            code: 代码内容
            language: 编程语言

        Returns:
            是否包含错误处理
        """
        error_handling_patterns = {
            'python': r'(try:|except |raise |assert )',
            'javascript': r'(try \{|catch|throw |\.catch\()',
            'typescript': r'(try \{|catch|throw |\.catch\()',
            'java': r'(try \{|catch|throws?|throw )',
        }

        pattern = error_handling_patterns.get(language.lower(), r'(try|catch|except|error)')
        return bool(re.search(pattern, code, re.IGNORECASE))

    def has_section(self, name: str) -> bool:
        """
        检查是否有指定章节

        Args:
            name: 章节名称

        Returns:
            是否存在该章节
        """
        return any(s.matches(name) for s in self.sections)

    def get_section_content(self, name: str) -> Optional[str]:
        """
        获取指定章节的内容

        Args:
            name: 章节名称

        Returns:
            章节内容，如果不存在则返回 None
        """
        for section in self.sections:
            if section.matches(name):
                return section.content
        return None

    def get_sections_by_level(self, level: int) -> List[Section]:
        """
        获取指定级别的所有章节

        Args:
            level: 标题级别 (1-6)

        Returns:
            该级别的章节列表
        """
        return [s for s in self.sections if s.level == level]

    @property
    def top_level_sections(self) -> List[Section]:
        """
        获取顶级章节（最高级别的标题）

        Returns:
            顶级章节列表
        """
        if not self.sections:
            return []

        min_level = min(s.level for s in self.sections)
        return self.get_sections_by_level(min_level)
