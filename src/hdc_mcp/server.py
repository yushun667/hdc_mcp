# src/hdc_mcp/server.py
"""
MCP 服务入口模块。
负责创建 FastMCP 实例，从各 tools 模块导入并注册所有工具，启动服务。
工具按功能分模块组织，共 24 个 MCP 工具。
"""
from mcp.server.fastmcp import FastMCP

from hdc_mcp.tools.device import (
    hdc_list_targets,
    hdc_target_connect,
    hdc_target_disconnect,
    hdc_target_reboot,
    hdc_target_mode,
    hdc_smode,
)
from hdc_mcp.tools.file import hdc_file_send, hdc_file_recv
from hdc_mcp.tools.app import hdc_app_install, hdc_app_uninstall
from hdc_mcp.tools.shell import hdc_shell
from hdc_mcp.tools.log import (
    hdc_hilog,
    hdc_hilog_clear,
    hdc_hilog_buffer_info,
    hdc_hilog_write_start,
    hdc_hilog_write_stop,
    hdc_hilog_write_query,
    hdc_hilog_privacy,
    hdc_hilog_kernel,
)
from hdc_mcp.tools.forward import hdc_fport_add, hdc_fport_rm, hdc_fport_list
from hdc_mcp.tools.server_tools import hdc_start_server, hdc_kill_server

# 创建全局 MCP 服务实例
mcp = FastMCP("hdc-mcp")

# 注册所有工具到 MCP 实例
# 设备管理（6个）
mcp.tool()(hdc_list_targets)
mcp.tool()(hdc_target_connect)
mcp.tool()(hdc_target_disconnect)
mcp.tool()(hdc_target_reboot)
mcp.tool()(hdc_target_mode)
mcp.tool()(hdc_smode)

# 文件传输（2个）
mcp.tool()(hdc_file_send)
mcp.tool()(hdc_file_recv)

# 应用管理（2个）
mcp.tool()(hdc_app_install)
mcp.tool()(hdc_app_uninstall)

# Shell 命令（1个，高权限工具）
mcp.tool()(hdc_shell)

# 日志（8个）
mcp.tool()(hdc_hilog)
mcp.tool()(hdc_hilog_clear)
mcp.tool()(hdc_hilog_buffer_info)
mcp.tool()(hdc_hilog_write_start)
mcp.tool()(hdc_hilog_write_stop)
mcp.tool()(hdc_hilog_write_query)
mcp.tool()(hdc_hilog_privacy)
mcp.tool()(hdc_hilog_kernel)

# 端口转发（3个）
mcp.tool()(hdc_fport_add)
mcp.tool()(hdc_fport_rm)
mcp.tool()(hdc_fport_list)

# 服务管理（2个）
mcp.tool()(hdc_start_server)
mcp.tool()(hdc_kill_server)


def main() -> None:
    """MCP 服务主入口，供 uvx/命令行调用。"""
    mcp.run()


if __name__ == "__main__":
    main()
