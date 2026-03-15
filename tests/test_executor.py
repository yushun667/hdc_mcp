# tests/test_executor.py
"""
executor 模块测试：验证 hdc 命令执行、超时处理、错误捕获。
"""
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from hdc_mcp.executor import run, ExecuteResult


class TestExecuteResult:
    """测试 ExecuteResult 数据结构。"""

    def test_default_timed_out_is_false(self):
        """timed_out 默认值为 False。"""
        result = ExecuteResult(stdout="ok", stderr="", returncode=0)
        assert result.timed_out is False

    def test_fields(self):
        """所有字段可正确赋值。"""
        result = ExecuteResult(stdout="out", stderr="err", returncode=1, timed_out=True)
        assert result.stdout == "out"
        assert result.stderr == "err"
        assert result.returncode == 1
        assert result.timed_out is True


class TestRun:
    """测试 run() 函数的各种场景。"""

    def test_successful_command(self):
        """正常命令执行返回 stdout 内容。"""
        mock_result = MagicMock()
        mock_result.stdout = "device_list\n"
        mock_result.stderr = ""
        mock_result.returncode = 0

        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", return_value=mock_result):
                result = run(["list", "targets"])

        assert result.stdout == "device_list\n"
        assert result.returncode == 0
        assert result.timed_out is False

    def test_hdc_not_found_returns_error(self):
        """hdc 未找到时返回描述性错误信息。"""
        with patch("hdc_mcp.executor.get_hdc_path", return_value=None):
            result = run(["list", "targets"])

        assert result.returncode == -1
        assert "HDC_PATH" in result.stderr
        assert result.timed_out is False

    def test_timeout_returns_timed_out_flag(self):
        """命令超时时 timed_out=True，returncode=-1。"""
        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="hdc", timeout=30)):
                result = run(["shell", "sleep 100"], timeout=1)

        assert result.timed_out is True
        assert result.returncode == -1

    def test_command_failure_returns_stderr(self):
        """命令失败时返回 stderr 内容和非零 returncode。"""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "[Fail] Connect failed"
        mock_result.returncode = 1

        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", return_value=mock_result):
                result = run(["tconn", "192.168.1.1:5555"])

        assert result.returncode == 1
        assert "Connect failed" in result.stderr

    def test_uses_custom_timeout(self):
        """run() 使用传入的 timeout 参数。"""
        mock_result = MagicMock(stdout="", stderr="", returncode=0)

        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", return_value=mock_result) as mock_subprocess:
                run(["list", "targets"], timeout=10)
                _, kwargs = mock_subprocess.call_args
                assert kwargs["timeout"] == 10
