# src/hdc_mcp/tools/app.py
"""
应用管理工具模块。
封装 hdc app install/uninstall 命令，支持 HAP 包安装和应用卸载，共 2 个 MCP 工具。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix


def hdc_app_install(
    hap_path: str,
    replace: bool = False,
    shared: bool = False,
    serial: str | None = None,
) -> str:
    """
    安装 HAP 包到设备。

    参数:
        hap_path: 本地 HAP 文件路径
        replace: True 时替换安装（对应 -r 参数）
        shared: True 时安装为共享包（对应 -s 参数）
        serial: 目标设备序列号，多设备时必须指定

    返回:
        安装结果字符串
    """
    args = serial_prefix(serial) + ["app", "install"]
    if replace:
        args.append("-r")
    if shared:
        args.append("-s")
    args.append(hap_path)
    return format_result(run(args))


def hdc_app_uninstall(
    bundle_name: str,
    shared: bool = False,
    serial: str | None = None,
) -> str:
    """
    从设备卸载应用。

    参数:
        bundle_name: 应用包名，如 com.example.myapp
        shared: True 时卸载共享包（对应 -s 参数）
        serial: 目标设备序列号，多设备时必须指定

    返回:
        卸载结果字符串
    """
    args = serial_prefix(serial) + ["app", "uninstall"]
    if shared:
        args.append("-s")
    args.append(bundle_name)
    return format_result(run(args))
