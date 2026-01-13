#!/usr/bin/env python3
"""
GitHub 技能下载器

支持从 GitHub URL 下载技能到本地缓存，便于评分系统分析

支持的 URL 格式：
- https://github.com/user/repo/tree/branch/path/to/skill
- https://github.com/user/repo/blob/branch/path/to/skill
"""

import re
import shutil
from pathlib import Path
from typing import Optional, Tuple
from urllib.parse import urlparse

import requests


class GitHubSkillFetcher:
    """GitHub 技能下载器"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        初始化下载器

        Args:
            cache_dir: 缓存目录，默认为系统临时目录
        """
        if cache_dir is None:
            import tempfile
            cache_dir = Path(tempfile.gettempdir()) / "skill_cache"

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def parse_github_url(self, url: str) -> dict:
        """
        解析 GitHub URL，提取必要信息

        支持的 URL 格式：
        - https://github.com/anthropics/claude-cookbooks/tree/main/skills/custom_skills/applying-brand-guidelines
        - https://github.com/user/repo/tree/branch/path/to/skill

        Args:
            url: GitHub URL

        Returns:
            包含 user, repo, branch, path, skill_name 的字典

        Raises:
            ValueError: 如果 URL 格式无效
        """
        # 解析 URL
        parsed = urlparse(url)

        # 正则匹配 GitHub URL
        # 支持 tree 和 blob 两种格式
        pattern = r'github\.com/([^/]+)/([^/]+)/(?:tree|blob)/([^/]+)/(.+)'
        match = re.search(pattern, url)

        if not match:
            raise ValueError(
                f"无效的 GitHub URL 格式: {url}\n"
                f"期望格式: https://github.com/user/repo/tree/branch/path/to/skill"
            )

        user, repo, branch, path = match.groups()

        return {
            'user': user,
            'repo': repo,
            'branch': branch,
            'path': path.rstrip('/'),
            'skill_name': path.split('/')[-1]
        }

    def get_raw_urls(self, url: str) -> Tuple[str, str, str]:
        """
        将 GitHub URL 转换为 Raw 内容 URL

        Args:
            url: GitHub 仓库 URL

        Returns:
            (skill_raw_url, metadata_raw_url, skill_name)
        """
        info = self.parse_github_url(url)

        # Raw URL 格式
        base_url = f"https://raw.githubusercontent.com/{info['user']}/{info['repo']}/{info['branch']}"

        skill_url = f"{base_url}/{info['path']}/SKILL.md"
        metadata_url = f"{base_url}/{info['path']}/metadata.json"

        return skill_url, metadata_url, info['skill_name']

    def download_file(self, url: str, dest_path: Path, description: str = "文件") -> bool:
        """
        下载单个文件

        Args:
            url: 下载 URL
            dest_path: 目标路径
            description: 文件描述（用于日志）

        Returns:
            是否成功下载
        """
        try:
            print(f"📥 下载 {description}: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            dest_path.write_text(response.text, encoding='utf-8')
            print(f"✅ {description} 下载成功")
            return True

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                print(f"⚠️  {description} 不存在（跳过）")
                return False
            else:
                print(f"❌ {description} 下载失败: {e}")
                raise
        except Exception as e:
            print(f"❌ {description} 下载失败: {e}")
            raise

    def download_skill(self, url: str) -> Path:
        """
        下载技能到缓存目录

        Args:
            url: GitHub 仓库 URL

        Returns:
            本地缓存路径
        """
        skill_url, metadata_url, skill_name = self.get_raw_urls(url)

        # 创建缓存目录
        cache_path = self.cache_dir / skill_name
        cache_path.mkdir(parents=True, exist_ok=True)

        # 下载 SKILL.md（必需）
        skill_file = cache_path / "SKILL.md"
        self.download_file(skill_url, skill_file, "SKILL.md")

        # 尝试下载 metadata.json（可选）
        metadata_file = cache_path / "metadata.json"
        self.download_file(metadata_url, metadata_file, "metadata.json")

        print(f"✅ 技能已缓存到: {cache_path}")
        return cache_path

    def clear_cache(self, skill_name: Optional[str] = None):
        """
        清理缓存

        Args:
            skill_name: 指定技能名称，None 表示清理全部
        """
        if skill_name:
            cache_path = self.cache_dir / skill_name
            if cache_path.exists():
                shutil.rmtree(cache_path)
                print(f"🗑️  已清理缓存: {skill_name}")
            else:
                print(f"⚠️  缓存不存在: {skill_name}")
        else:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
                print(f"🗑️  已清理全部缓存")
            else:
                print(f"⚠️  缓存目录不存在")

    def get_cache_path(self, skill_name: str) -> Optional[Path]:
        """
        获取技能缓存路径

        Args:
            skill_name: 技能名称

        Returns:
            缓存路径，如果不存在则返回 None
        """
        cache_path = self.cache_dir / skill_name
        if cache_path.exists() and (cache_path / "SKILL.md").exists():
            return cache_path
        return None
