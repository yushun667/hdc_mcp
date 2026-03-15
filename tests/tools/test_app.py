# tests/tools/test_app.py
"""
应用管理工具测试：验证 app install/uninstall 命令参数构建。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.app import hdc_app_install, hdc_app_uninstall

def ok(stdout="[成功]"):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcAppInstall:
    def test_basic_install(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap")
            mock_run.assert_called_once_with(["app", "install", "/tmp/app.hap"])

    def test_install_with_replace(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap", replace=True)
            mock_run.assert_called_once_with(["app", "install", "-r", "/tmp/app.hap"])

    def test_install_with_shared(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap", shared=True)
            mock_run.assert_called_once_with(["app", "install", "-s", "/tmp/app.hap"])

    def test_install_with_serial(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "app", "install", "/tmp/app.hap"])


class TestHdcAppUninstall:
    def test_basic_uninstall(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_uninstall(bundle_name="com.example.app")
            mock_run.assert_called_once_with(["app", "uninstall", "com.example.app"])

    def test_uninstall_shared(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_uninstall(bundle_name="com.example.app", shared=True)
            mock_run.assert_called_once_with(["app", "uninstall", "-s", "com.example.app"])
