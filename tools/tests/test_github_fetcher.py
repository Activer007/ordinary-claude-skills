#!/usr/bin/env python3
"""
测试 GitHubFetcher 功能
使用 unittest.mock 模拟网络请求，避免实际的网络调用
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import requests

from analyzer.github_fetcher import GitHubSkillFetcher


class TestGitHubURLParsing:
    """测试 GitHub URL 解析"""

    @pytest.fixture
    def fetcher(self):
        """创建 fetcher 实例"""
        return GitHubSkillFetcher()

    def test_parse_valid_url_with_tree(self, fetcher):
        """测试解析有效的 tree 格式 URL"""
        url = "https://github.com/anthropics/claude-cookbooks/tree/main/skills/test"
        info = fetcher.parse_github_url(url)

        assert info['user'] == 'anthropics'
        assert info['repo'] == 'claude-cookbooks'
        assert info['branch'] == 'main'
        assert info['path'] == 'skills/test'
        assert info['skill_name'] == 'test'

    def test_parse_valid_url_with_blob(self, fetcher):
        """测试解析有效的 blob 格式 URL"""
        url = "https://github.com/user/repo/blob/develop/path/to/skill"
        info = fetcher.parse_github_url(url)

        assert info['user'] == 'user'
        assert info['repo'] == 'repo'
        assert info['branch'] == 'develop'
        assert info['path'] == 'path/to/skill'

    def test_parse_branch_with_slashes(self, fetcher):
        """测试解析分支名包含斜杠的 URL

        注意：由于无法区分分支名中的斜杠和路径分隔符，
        我们采用启发式方法：在第一个斜杠处分割。
        这意味着 'feature/new-api' 可能会被解析为 branch='feature', path='new-api/...'
        这是无API情况下的已知限制。
        """
        url = "https://github.com/user/repo/tree/feature/new-api/skills/test"
        info = fetcher.parse_github_url(url)

        # 使用启发式分割：第一个斜杠之前是分支，之后是路径
        assert info['branch'] == 'feature'
        assert info['path'] == 'new-api/skills/test'

    def test_parse_root_path(self, fetcher):
        """测试解析仓库根路径 URL"""
        url = "https://github.com/user/repo/tree/main"
        info = fetcher.parse_github_url(url)

        assert info['branch'] == 'main'
        assert info['path'] == ''

    def test_parse_invalid_url_not_github(self, fetcher):
        """测试解析非 GitHub URL"""
        with pytest.raises(ValueError, match="无效的 GitHub URL"):
            fetcher.parse_github_url("https://example.com/not-github")

    def test_parse_invalid_url_missing_parts(self, fetcher):
        """测试解析缺少必要部分的 URL"""
        with pytest.raises(ValueError, match="无效的 GitHub URL"):
            fetcher.parse_github_url("https://github.com/user/repo")

    def test_get_raw_urls_conversion(self, fetcher):
        """测试将 GitHub URL 转换为 Raw URL"""
        url = "https://github.com/anthropics/claude-cookbooks/tree/main/skills/test"
        skill_url, metadata_url, skill_name = fetcher.get_raw_urls(url)

        assert skill_url == "https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/skills/test/SKILL.md"
        assert metadata_url == "https://raw.githubusercontent.com/anthropics/claude-cookbooks/main/skills/test/metadata.json"
        assert skill_name == "test"


class TestFileDownload:
    """测试文件下载功能"""

    @pytest.fixture
    def fetcher(self, tmp_path):
        """创建使用临时目录的 fetcher 实例"""
        return GitHubSkillFetcher(cache_dir=tmp_path)

    @patch('analyzer.github_fetcher.requests.get')
    def test_download_skill_success(self, mock_get, fetcher):
        """测试成功下载技能"""
        # 模拟 HTTP 响应
        mock_response = Mock()
        mock_response.text = "# Test Skill\n\nContent here"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        # 执行下载
        url = "https://github.com/user/repo/tree/main/skill-name"
        cache_path = fetcher.download_skill(url)

        # 验证文件已创建
        assert (cache_path / "SKILL.md").exists()
        content = (cache_path / "SKILL.md").read_text()
        assert "Test Skill" in content
        assert "Content here" in content

    @patch('analyzer.github_fetcher.requests.get')
    def test_download_skill_404_error(self, mock_get, fetcher):
        """测试处理 SKILL.md 404 错误"""
        # 模拟 404 响应
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = \
            requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value = mock_response

        # 应该抛出 FileNotFoundError
        url = "https://github.com/user/repo/tree/main/skill-name"
        with pytest.raises(FileNotFoundError, match="SKILL.md.*下载失败或不存在"):
            fetcher.download_skill(url)

    @patch('analyzer.github_fetcher.requests.get')
    def test_download_network_timeout(self, mock_get, fetcher):
        """测试网络超时处理"""
        mock_get.side_effect = requests.exceptions.Timeout()

        url = "https://github.com/user/repo/tree/main/skill"
        with pytest.raises(requests.exceptions.Timeout):
            fetcher.download_skill(url)

    @patch('analyzer.github_fetcher.requests.get')
    def test_download_metadata_404_is_ok(self, mock_get, fetcher):
        """测试 metadata.json 404 不影响下载"""
        # 第一个调用返回成功（SKILL.md）
        # 第二个调用返回 404（metadata.json）
        success_response = Mock()
        success_response.text = "# Skill"
        success_response.raise_for_status = Mock()

        not_found_response = Mock()
        not_found_response.status_code = 404
        not_found_response.raise_for_status.side_effect = \
            requests.exceptions.HTTPError(response=not_found_response)

        mock_get.side_effect = [success_response, not_found_response]

        # 应该成功，metadata.json 是可选的
        url = "https://github.com/user/repo/tree/main/skill"
        cache_path = fetcher.download_skill(url)

        assert (cache_path / "SKILL.md").exists()
        assert not (cache_path / "metadata.json").exists()


class TestCaching:
    """测试缓存机制"""

    @pytest.fixture
    def fetcher(self, tmp_path):
        """创建 fetcher 实例"""
        return GitHubSkillFetcher(cache_dir=tmp_path)

    @patch('analyzer.github_fetcher.requests.get')
    def test_cache_reuse_on_second_download(self, mock_get, fetcher):
        """测试第二次下载使用缓存"""
        mock_response = Mock()
        mock_response.text = "# Cached Skill"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = "https://github.com/user/repo/tree/main/skill"

        # 第一次下载
        cache_path1 = fetcher.download_skill(url)
        assert mock_get.call_count == 2  # SKILL.md + metadata.json

        # 第二次下载（应该使用缓存）
        cache_path2 = fetcher.download_skill(url)
        assert mock_get.call_count == 2  # 没有增加

        assert cache_path1 == cache_path2

    @patch('analyzer.github_fetcher.requests.get')
    def test_force_refresh_bypasses_cache(self, mock_get, fetcher):
        """测试 force_refresh 强制重新下载"""
        mock_response = Mock()
        mock_response.text = "# Refreshed Skill"
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response

        url = "https://github.com/user/repo/tree/main/skill"

        # 第一次下载
        fetcher.download_skill(url)
        first_call_count = mock_get.call_count

        # 强制刷新
        fetcher.download_skill(url, force_refresh=True)
        assert mock_get.call_count > first_call_count

    def test_clear_cache_by_name(self, fetcher, tmp_path):
        """测试清理特定技能缓存"""
        # 创建缓存
        cache_dir = tmp_path / "test_skill"
        cache_dir.mkdir()
        (cache_dir / "SKILL.md").write_text("# Test")

        # 清理缓存
        fetcher.clear_cache("test_skill")

        assert not cache_dir.exists()

    def test_clear_all_cache(self, fetcher, tmp_path):
        """测试清理全部缓存"""
        # 创建多个缓存
        (tmp_path / "skill1").mkdir()
        (tmp_path / "skill1" / "SKILL.md").write_text("#1")
        (tmp_path / "skill2").mkdir()
        (tmp_path / "skill2" / "SKILL.md").write_text("#2")

        # 清理全部
        fetcher.clear_cache()

        assert not (tmp_path / "skill1").exists()
        assert not (tmp_path / "skill2").exists()

    def test_get_cache_path_valid(self, fetcher, tmp_path):
        """测试获取有效的缓存路径"""
        cache_dir = tmp_path / "test_skill"
        cache_dir.mkdir()
        (cache_dir / "SKILL.md").write_text("# Test")

        result = fetcher.get_cache_path("test_skill")
        assert result == cache_dir

    def test_get_cache_path_missing_skill_md(self, fetcher, tmp_path):
        """测试缓存目录存在但缺少 SKILL.md"""
        cache_dir = tmp_path / "test_skill"
        cache_dir.mkdir()
        # 不创建 SKILL.md

        result = fetcher.get_cache_path("test_skill")
        assert result is None


class TestIntegration:
    """集成测试"""

    @patch('analyzer.github_fetcher.requests.get')
    def test_full_download_workflow(self, mock_get):
        """测试完整的下载工作流"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            fetcher = GitHubSkillFetcher(cache_dir=Path(tmp_dir))

            # 模拟响应
            mock_response = Mock()
            mock_response.text = "---\nname: test-skill\n---\n\n# Test Skill\n"
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response

            # 下载
            url = "https://github.com/user/repo/tree/main/skills/test"
            cache_path = fetcher.download_skill(url)

            # 验证完整文件结构
            assert cache_path.exists()
            assert (cache_path / "SKILL.md").exists()

            content = (cache_path / "SKILL.md").read_text()
            assert "test-skill" in content
            assert "Test Skill" in content

    @patch('analyzer.github_fetcher.requests.get')
    def test_error_cleanup_on_failure(self, mock_get):
        """测试失败时清理缓存目录"""
        with tempfile.TemporaryDirectory() as tmp_dir:
            fetcher = GitHubSkillFetcher(cache_dir=Path(tmp_dir))

            # 模拟 404 错误
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = \
                requests.exceptions.HTTPError(response=mock_response)
            mock_get.return_value = mock_response

            url = "https://github.com/user/repo/tree/main/skill"

            # 应该失败
            with pytest.raises(FileNotFoundError):
                fetcher.download_skill(url)

            # 缓存目录应该被清理
            cache_dir = fetcher.cache_dir / "skill"
            assert not cache_dir.exists()
