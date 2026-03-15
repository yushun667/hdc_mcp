# tests/test_server.py
"""
server 模块测试：验证所有工具已注册到 MCP 实例。
"""
from hdc_mcp.server import mcp


class TestMcpToolsRegistered:
    """验证所有 24 个工具都已注册到 MCP 实例。"""

    def _get_tool_names(self):
        # FastMCP 将工具存储在内部字典中
        return list(mcp._tool_manager._tools.keys())

    def test_device_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_list_targets", "hdc_target_connect", "hdc_target_disconnect",
                     "hdc_target_reboot", "hdc_target_mode", "hdc_smode"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_file_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_file_send", "hdc_file_recv"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_app_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_app_install", "hdc_app_uninstall"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_shell_tools_registered(self):
        names = self._get_tool_names()
        assert "hdc_shell" in names

    def test_log_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_hilog", "hdc_hilog_clear", "hdc_hilog_buffer_info",
                     "hdc_hilog_write_start", "hdc_hilog_write_stop", "hdc_hilog_write_query",
                     "hdc_hilog_privacy", "hdc_hilog_kernel"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_forward_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_fport_add", "hdc_fport_rm", "hdc_fport_list"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_server_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_start_server", "hdc_kill_server"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_total_tool_count(self):
        names = self._get_tool_names()
        assert len(names) == 24, f"预期 24 个工具，实际 {len(names)} 个：{names}"
