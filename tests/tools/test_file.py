# tests/tools/test_file.py
"""
文件传输工具测试：验证 file send/recv 命令参数构建。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.file import hdc_file_send, hdc_file_recv

def ok(stdout="[成功]"):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcFileSend:
    def test_basic_send(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_send(local="/tmp/app.hap", remote="/data/local/tmp/app.hap")
            mock_run.assert_called_once_with(["file", "send", "/tmp/app.hap", "/data/local/tmp/app.hap"])

    def test_send_with_serial(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_send(local="/tmp/app.hap", remote="/data/local/tmp/app.hap", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "file", "send", "/tmp/app.hap", "/data/local/tmp/app.hap"])


class TestHdcFileRecv:
    def test_basic_recv(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_recv(remote="/data/local/tmp/log.txt", local="/tmp/log.txt")
            mock_run.assert_called_once_with(["file", "recv", "/data/local/tmp/log.txt", "/tmp/log.txt"])

    def test_recv_with_serial(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_recv(remote="/data/local/tmp/log.txt", local="/tmp/log.txt", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "file", "recv", "/data/local/tmp/log.txt", "/tmp/log.txt"])
