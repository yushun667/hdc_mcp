# src/hdc_mcp/tools/file.py
"""
文件传输工具模块。
封装 hdc file send/recv 命令，支持本地与设备之间的文件双向传输，共 2 个 MCP 工具。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix


def hdc_file_send(local: str, remote: str, serial: str | None = None) -> str:
    """
    推送本地文件或目录到设备。

    参数:
        local: 本地文件或目录路径（绝对路径）
        remote: 设备上的目标路径
        serial: 目标设备序列号，多设备时必须指定

    返回:
        传输结果字符串
    """
    args = serial_prefix(serial) + ["file", "send", local, remote]
    return format_result(run(args))


def hdc_file_recv(remote: str, local: str, serial: str | None = None) -> str:
    """
    从设备拉取文件或目录到本地。

    参数:
        remote: 设备上的源文件或目录路径
        local: 本地目标路径
        serial: 目标设备序列号，多设备时必须指定

    返回:
        传输结果字符串
    """
    args = serial_prefix(serial) + ["file", "recv", remote, local]
    return format_result(run(args))
