# tests/tools/test_log.py
"""
日志工具测试：验证 hilog 命令的全量过滤参数构建和约束校验。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.log import (
    hdc_hilog, hdc_hilog_clear, hdc_hilog_buffer_info,
    hdc_hilog_write_start, hdc_hilog_write_stop, hdc_hilog_write_query,
    hdc_hilog_privacy, hdc_hilog_kernel,
)
import pytest

def ok(stdout="log output"):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcHilog:
    def test_requires_lines_or_timeout(self):
        """lines 和 timeout 都未提供时，使用默认 lines=200。"""
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog()
            args = mock_run.call_args[0][0]
            assert "-n" in args or "--head" in args  # 默认限制行数

    def test_filter_by_level(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(level="ERROR", lines=50)
            args = mock_run.call_args[0][0]
            assert "-l" in args
            assert "ERROR" in args

    def test_filter_by_tag(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(tag="MyApp", lines=50)
            args = mock_run.call_args[0][0]
            assert "-t" in args
            assert "MyApp" in args

    def test_filter_by_pid(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(pid=1234, lines=50)
            args = mock_run.call_args[0][0]
            assert "-P" in args
            assert "1234" in args

    def test_invalid_level_returns_error(self):
        result = hdc_hilog(level="VERBOSE", lines=50)
        assert "错误" in result

    def test_with_serial(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(serial="SN001", lines=10)
            args = mock_run.call_args[0][0]
            # serial 的 -t 必须在 hilog 之前
            t_index = args.index("-t")
            hilog_index = args.index("hilog")
            assert t_index < hilog_index
            assert args[t_index + 1] == "SN001"


class TestHdcHilogClear:
    def test_clear(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_clear()
            mock_run.assert_called_once_with(["hilog", "-r"])


class TestHdcHilogBufferInfo:
    def test_buffer_info(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_buffer_info()
            mock_run.assert_called_once_with(["hilog", "-g"])


class TestHdcHilogWrite:
    def test_write_start(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_write_start()
            mock_run.assert_called_once_with(["hilog", "-w", "start"])

    def test_write_stop(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_write_stop()
            mock_run.assert_called_once_with(["hilog", "-w", "stop"])

    def test_write_query(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_write_query()
            mock_run.assert_called_once_with(["hilog", "-w", "query"])


class TestHdcHilogPrivacy:
    def test_enable_privacy(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_privacy(enable=True)
            mock_run.assert_called_once_with(["hilog", "-p", "on"])

    def test_disable_privacy(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_privacy(enable=False)
            mock_run.assert_called_once_with(["hilog", "-p", "off"])


class TestHdcHilogKernel:
    def test_enable_kernel(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_kernel(enable=True)
            mock_run.assert_called_once_with(["hilog", "-k", "on"])

    def test_disable_kernel(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_kernel(enable=False)
            mock_run.assert_called_once_with(["hilog", "-k", "off"])
