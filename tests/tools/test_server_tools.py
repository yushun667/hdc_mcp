# tests/tools/test_server_tools.py
"""
服务管理工具测试：验证 hdc start/kill 命令。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.server_tools import hdc_start_server, hdc_kill_server

def ok():
    return ExecuteResult(stdout="", stderr="", returncode=0)


class TestHdcStartServer:
    def test_start(self):
        with patch("hdc_mcp.tools.server_tools.run", return_value=ok()) as mock_run:
            hdc_start_server()
            mock_run.assert_called_once_with(["start"])


class TestHdcKillServer:
    def test_kill(self):
        with patch("hdc_mcp.tools.server_tools.run", return_value=ok()) as mock_run:
            hdc_kill_server()
            mock_run.assert_called_once_with(["kill"])
