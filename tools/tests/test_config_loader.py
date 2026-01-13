#!/usr/bin/env python3
"""
配置加载器单元测试

测试 ScoringConfig 类的功能：
- 配置文件加载
- 参数获取
- 默认值回退
- 向后兼容

Created: 2026-01-13
"""

import pytest
import yaml
from pathlib import Path
import tempfile
import os

from analyzer.config_loader import ScoringConfig, get_config


class TestScoringConfig:
    """ScoringConfig 类的测试"""

    @pytest.fixture
    def temp_config_file(self):
        """创建临时配置文件用于测试"""
        config_content = {
            'content_quality': {
                'clarity': {
                    'use_cases': {'max_value': 5, 'max_score': 5}
                },
                'technical_depth': {
                    'code_blocks': {'max_value': 8, 'max_score': 7},
                    'best_practices': {'max_value': 5, 'max_score': 4}
                },
                'documentation': {
                    'sections': {'max_value': 10, 'max_score': 6},
                    'examples': {'max_value': 5, 'max_score': 4}
                }
            },
            'technical_implementation': {
                'code_quality': {
                    'code_block_count': {'max_value': 5, 'max_score': 5}
                }
            },
            'general': {
                'default_max_value': 5,
                'default_max_score': 5,
                'backward_compatible': True,
                'debug_mode': False
            }
        }

        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(config_content, f)
            temp_path = f.name

        yield temp_path

        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)

    def test_load_config_from_file(self, temp_config_file):
        """测试从文件加载配置"""
        config = ScoringConfig(temp_config_file)

        assert config.config is not None
        assert 'content_quality' in config.config
        assert 'technical_implementation' in config.config

    def test_get_smooth_params_success(self, temp_config_file):
        """测试成功获取 smooth_score 参数"""
        config = ScoringConfig(temp_config_file)

        # 测试获取 use_cases 参数
        params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
        assert params == {'max_value': 5, 'max_score': 5}

        # 测试获取 code_blocks 参数
        params = config.get_smooth_params('content_quality', 'technical_depth', 'code_blocks')
        assert params == {'max_value': 8, 'max_score': 7}

        # 测试获取 best_practices 参数
        params = config.get_smooth_params('content_quality', 'technical_depth', 'best_practices')
        assert params == {'max_value': 5, 'max_score': 4}

    def test_get_smooth_params_with_invalid_path(self, temp_config_file):
        """测试使用无效路径获取参数（应返回默认值）"""
        config = ScoringConfig(temp_config_file)

        # 使用不存在的路径
        params = config.get_smooth_params('invalid', 'path', 'here')
        assert params == {'max_value': 5, 'max_score': 5}  # 默认值

    def test_get_method(self, temp_config_file):
        """测试通用的 get 方法"""
        config = ScoringConfig(temp_config_file)

        # 测试获取 debug_mode
        debug_mode = config.get('general', 'debug_mode')
        assert debug_mode is False

        # 测试获取不存在的配置（返回默认值）
        value = config.get('nonexistent', 'key', default='default_value')
        assert value == 'default_value'

    def test_load_nonexistent_config_file(self):
        """测试加载不存在的配置文件（应使用内置默认配置）"""
        config = ScoringConfig('/nonexistent/path/config.yml')

        assert config.config is not None
        # 应该回退到默认配置
        params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
        assert params == {'max_value': 5, 'max_score': 5}

    def test_backward_compatibility(self, temp_config_file):
        """测试向后兼容性"""
        config = ScoringConfig(temp_config_file)

        # 即使配置路径不存在，也应该返回默认值
        params = config.get_smooth_params('new_category', 'new_subcategory', 'new_param')
        assert params == {'max_value': 5, 'max_score': 5}

    def test_empty_config_file(self):
        """测试空配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write('')  # 空文件
            temp_path = f.name

        try:
            config = ScoringConfig(temp_path)
            # 应该使用默认配置
            params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
            assert params == {'max_value': 5, 'max_score': 5}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_malformed_config_file(self):
        """测试格式错误的配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            f.write('invalid: yaml: content: [')  # 无效的 YAML
            temp_path = f.name

        try:
            config = ScoringConfig(temp_path)
            # 应该回退到默认配置
            params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
            assert params == {'max_value': 5, 'max_score': 5}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_reload_config(self, temp_config_file):
        """测试重新加载配置"""
        config = ScoringConfig(temp_config_file)

        # 初始值
        params1 = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
        assert params1 == {'max_value': 5, 'max_score': 5}

        # 修改配置文件
        with open(temp_config_file, 'r') as f:
            config_data = yaml.safe_load(f)
        config_data['content_quality']['clarity']['use_cases']['max_value'] = 10
        with open(temp_config_file, 'w') as f:
            yaml.dump(config_data, f)

        # 重新加载
        config.reload()

        # 验证新值
        params2 = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
        assert params2 == {'max_value': 10, 'max_score': 5}


class TestGlobalConfigSingleton:
    """测试全局配置单例"""

    def test_get_config_singleton(self):
        """测试 get_config 返回单例"""
        config1 = get_config()
        config2 = get_config()

        # 应该是同一个实例
        assert config1 is config2

    def test_get_config_reload(self):
        """测试强制重新加载配置"""
        config1 = get_config()
        config2 = get_config(reload=True)

        # reload=True 时会创建新实例
        # 但由于都是加载相同的配置文件，内容应该相同
        params1 = config1.get_smooth_params('content_quality', 'clarity', 'use_cases')
        params2 = config2.get_smooth_params('content_quality', 'clarity', 'use_cases')

        assert params1 == params2


class TestConfigMerging:
    """测试配置合并功能"""

    def test_merge_configs(self):
        """测试配置字典合并"""
        config = ScoringConfig()

        default = {
            'a': {'b': 1, 'c': 2},
            'd': 3
        }
        loaded = {
            'a': {'b': 10},  # 覆盖 b
            'e': 4           # 新增 e
        }

        merged = config._merge_configs(default, loaded)

        assert merged['a']['b'] == 10  # 覆盖
        assert merged['a']['c'] == 2   # 保留默认值
        assert merged['d'] == 3        # 保留默认值
        assert merged['e'] == 4        # 新增

    def test_partial_config_override(self):
        """测试部分配置覆盖"""
        # 创建只包含部分配置的临时文件
        partial_config = {
            'content_quality': {
                'clarity': {
                    'use_cases': {'max_value': 10, 'max_score': 8}  # 自定义值
                }
                # 其他配置项缺失
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(partial_config, f)
            temp_path = f.name

        try:
            config = ScoringConfig(temp_path)

            # 自定义的参数应该使用新值
            params1 = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
            assert params1 == {'max_value': 10, 'max_score': 8}

            # 未定义的参数应该使用默认值
            params2 = config.get_smooth_params('content_quality', 'technical_depth', 'code_blocks')
            assert params2 == {'max_value': 8, 'max_score': 7}
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestConfigValidation:
    """测试配置验证"""

    def test_missing_required_fields(self):
        """测试缺少必需字段的配置"""
        invalid_config = {
            'content_quality': {
                'clarity': {
                    'use_cases': {'max_value': 5}  # 缺少 max_score
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            config = ScoringConfig(temp_path)

            # 缺少必需字段时，应该返回默认值
            params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
            assert params == {'max_value': 5, 'max_score': 5}  # 默认值
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_non_dict_value(self):
        """测试非字典值的配置"""
        invalid_config = {
            'content_quality': {
                'clarity': {
                    'use_cases': 'not_a_dict'  # 应该是字典，但是字符串
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as f:
            yaml.dump(invalid_config, f)
            temp_path = f.name

        try:
            config = ScoringConfig(temp_path)

            # 非字典值时，应该返回默认值
            params = config.get_smooth_params('content_quality', 'clarity', 'use_cases')
            assert params == {'max_value': 5, 'max_score': 5}  # 默认值
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
