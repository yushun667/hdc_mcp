# src/hdc_mcp/tools/forward.py
"""
端口转发工具模块。
封装 hdc fport 命令，支持 TCP 端口转发规则的添加、删除和查询，共 3 个 MCP 工具。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix


def hdc_fport_add(local_port: int, remote_port: int, serial: str | None = None) -> str:
    """
    添加 TCP 端口转发规则，将本地端口映射到设备端口。

    参数:
        local_port: 本地监听端口号
        remote_port: 设备上的目标端口号
        serial: 目标设备序列号，多设备时必须指定

    返回:
        操作结果字符串
    """
    args = serial_prefix(serial) + ["fport", f"tcp:{local_port}", f"tcp:{remote_port}"]
    return format_result(run(args))


def hdc_fport_rm(local_port: int, remote_port: int, serial: str | None = None) -> str:
    """
    删除指定的 TCP 端口转发规则。

    参数:
        local_port: 本地端口号
        remote_port: 设备端口号
        serial: 目标设备序列号

    返回:
        操作结果字符串
    """
    args = serial_prefix(serial) + ["fport", "rm", f"tcp:{local_port}", f"tcp:{remote_port}"]
    return format_result(run(args))


def hdc_fport_list(serial: str | None = None) -> str:
    """
    列出所有当前端口转发规则。

    参数:
        serial: 目标设备序列号

    返回:
        端口转发规则列表字符串
    """
    args = serial_prefix(serial) + ["fport", "ls"]
    return format_result(run(args))
