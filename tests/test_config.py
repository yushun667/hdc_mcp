# tests/test_config.py
"""
config 模块测试：验证跨平台 hdc 路径解析逻辑和环境变量配置。
"""
import os
import platform
from unittest.mock import patch, MagicMock
import pytest
from hdc_mcp.config import get_hdc_path, get_timeout


class TestGetHdcPath:
    """测试 hdc 可执行文件路径解析逻辑。"""

    def test_env_var_takes_highest_priority(self, tmp_path):
        """HDC_PATH 环境变量优先级最高，即使该路径存在也应直接返回。"""
        fake_hdc = tmp_path / "hdc"
        fake_hdc.touch()
        with patch.dict(os.environ, {"HDC_PATH": str(fake_hdc)}):
            assert get_hdc_path() == str(fake_hdc)

    def test_env_var_not_set_falls_back_to_platform(self, tmp_path):
        """未设置 HDC_PATH 时，回退到 macOS 平台默认路径。"""
        fake_hdc = tmp_path / "hdc"
        fake_hdc.touch()
        with patch.dict(os.environ, {}, clear=True):
            with patch("platform.system", return_value="Darwin"):
                with patch("glob.glob", return_value=[str(fake_hdc)]):
                    result = get_hdc_path()
                    assert result == str(fake_hdc)

    def test_returns_none_when_hdc_not_found(self):
        """找不到 hdc 时返回 None。"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which", return_value=None):
                with patch("glob.glob", return_value=[]):
                    assert get_hdc_path() is None


class TestGetTimeout:
    """测试超时配置读取。"""

    def test_default_timeout(self):
        """未设置 HDC_TIMEOUT 时返回默认值 30。"""
        with patch.dict(os.environ, {}, clear=True):
            assert get_timeout() == 30

    def test_custom_timeout_from_env(self):
        """HDC_TIMEOUT 环境变量覆盖默认值。"""
        with patch.dict(os.environ, {"HDC_TIMEOUT": "60"}):
            assert get_timeout() == 60
