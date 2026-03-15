# tests/tools/test_forward.py
"""
端口转发工具测试：验证 fport 命令参数构建。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.forward import hdc_fport_add, hdc_fport_rm, hdc_fport_list

def ok(stdout=""):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcFportAdd:
    def test_add_port_forward(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok()) as mock_run:
            hdc_fport_add(local_port=8080, remote_port=8080)
            mock_run.assert_called_once_with(["fport", "tcp:8080", "tcp:8080"])

    def test_add_with_serial(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok()) as mock_run:
            hdc_fport_add(local_port=8080, remote_port=9090, serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "fport", "tcp:8080", "tcp:9090"])


class TestHdcFportRm:
    def test_remove_port_forward(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok()) as mock_run:
            hdc_fport_rm(local_port=8080, remote_port=8080)
            mock_run.assert_called_once_with(["fport", "rm", "tcp:8080", "tcp:8080"])


class TestHdcFportList:
    def test_list_rules(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok("tcp:8080 tcp:8080")) as mock_run:
            result = hdc_fport_list()
            mock_run.assert_called_once_with(["fport", "ls"])
            assert "8080" in result
