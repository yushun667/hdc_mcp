# src/hdc_mcp/tools/server_tools.py
"""
服务管理工具模块。
封装 hdc 服务端的启动和停止操作，共 2 个 MCP 工具。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result


def hdc_start_server() -> str:
    """
    启动 hdc 服务端守护进程。

    返回:
        启动结果字符串
    """
    return format_result(run(["start"]))


def hdc_kill_server() -> str:
    """
    停止 hdc 服务端守护进程。

    返回:
        停止结果字符串
    """
    return format_result(run(["kill"]))
