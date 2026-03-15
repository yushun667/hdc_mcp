# src/hdc_mcp/tools/device.py
"""
设备管理工具模块。
封装 hdc 设备连接、断开、重启、模式切换等操作，共 6 个 MCP 工具。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix


def hdc_list_targets(verbose: bool = False) -> str:
    """
    列出所有已连接的 HarmonyOS 设备。

    参数:
        verbose: 是否显示详细设备信息（对应 hdc list targets -v）

    返回:
        设备列表字符串
    """
    args = ["list", "targets"]
    if verbose:
        args.append("-v")
    return format_result(run(args))


def hdc_target_connect(address: str) -> str:
    """
    通过 TCP/IP 连接网络设备。

    参数:
        address: 设备地址，格式为 host:port，如 192.168.1.100:5555

    返回:
        连接结果字符串
    """
    return format_result(run(["tconn", address]))


def hdc_target_disconnect(address: str | None = None) -> str:
    """
    断开网络设备连接。

    参数:
        address: 设备地址（host:port），None 时断开所有网络设备

    返回:
        断开结果字符串
    """
    args = ["tdisconn"]
    if address is not None:
        args.append(address)
    return format_result(run(args))


def hdc_target_reboot(serial: str) -> str:
    """
    重启指定设备。

    参数:
        serial: 设备序列号（可通过 hdc_list_targets 获取）

    返回:
        重启结果字符串
    """
    return format_result(run(serial_prefix(serial) + ["target", "boot"]))


def hdc_target_mode(mode: str) -> str:
    """
    切换设备连接模式。

    参数:
        mode: 连接模式，只接受 "usb" 或 "tcp"

    返回:
        切换结果字符串
    """
    if mode not in ("usb", "tcp"):
        return f"[错误] mode 参数无效：{mode!r}，只接受 'usb' 或 'tcp'"
    return format_result(run(["tmode", mode]))


def hdc_smode(reset: bool = False) -> str:
    """
    切换 hdc 服务器权限模式。

    参数:
        reset: True 时重置为默认权限模式（对应 hdc smode -r）

    返回:
        操作结果字符串
    """
    args = ["smode"]
    if reset:
        args.append("-r")
    return format_result(run(args))
