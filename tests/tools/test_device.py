# tests/tools/test_device.py
"""
设备管理工具测试：验证各工具正确构建 hdc 命令参数。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.device import (
    hdc_list_targets, hdc_target_connect, hdc_target_disconnect,
    hdc_target_reboot, hdc_target_mode, hdc_smode,
)

# 成功结果的 mock 工厂
def ok(stdout=""):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcListTargets:
    def test_basic_call(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok("SN001\tUSB")) as mock_run:
            result = hdc_list_targets(verbose=False)
            mock_run.assert_called_once_with(["list", "targets"])
            assert "SN001" in result

    def test_verbose_flag(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_list_targets(verbose=True)
            mock_run.assert_called_once_with(["list", "targets", "-v"])


class TestHdcTargetConnect:
    def test_connect_address(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok("Connect OK")) as mock_run:
            result = hdc_target_connect(address="192.168.1.100:5555")
            mock_run.assert_called_once_with(["tconn", "192.168.1.100:5555"])
            assert "Connect OK" in result


class TestHdcTargetDisconnect:
    def test_disconnect_with_address(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_disconnect(address="192.168.1.100:5555")
            mock_run.assert_called_once_with(["tdisconn", "192.168.1.100:5555"])

    def test_disconnect_all(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_disconnect(address=None)
            mock_run.assert_called_once_with(["tdisconn"])


class TestHdcTargetReboot:
    def test_reboot_with_serial(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_reboot(serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "target", "boot"])


class TestHdcTargetMode:
    def test_usb_mode(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_mode(mode="usb")
            mock_run.assert_called_once_with(["tmode", "usb"])

    def test_tcp_mode(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_mode(mode="tcp")
            mock_run.assert_called_once_with(["tmode", "tcp"])

    def test_invalid_mode_raises(self):
        result = hdc_target_mode(mode="invalid")
        assert "错误" in result or "invalid" in result


class TestHdcSmode:
    def test_smode_basic(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_smode(reset=False)
            mock_run.assert_called_once_with(["smode"])

    def test_smode_reset(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_smode(reset=True)
            mock_run.assert_called_once_with(["smode", "-r"])
