# tests/tools/test_shell.py
"""
Shell 工具测试：验证 shell 命令透传和高权限工具描述。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.shell import hdc_shell

def ok(stdout=""):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcShell:
    def test_basic_shell_command(self):
        with patch("hdc_mcp.tools.shell.run", return_value=ok("total 0")) as mock_run:
            result = hdc_shell(command="ls /data")
            mock_run.assert_called_once_with(["shell", "ls /data"])
            assert "total 0" in result

    def test_shell_with_serial(self):
        with patch("hdc_mcp.tools.shell.run", return_value=ok()) as mock_run:
            hdc_shell(command="ls", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "shell", "ls"])

    def test_empty_command_returns_error(self):
        result = hdc_shell(command="")
        assert "错误" in result
