# src/hdc_mcp/tools/shell.py
"""
Shell 命令工具模块。
封装 hdc shell 命令，支持在设备上执行任意 shell 命令，共 1 个 MCP 工具。
⚠️ 高权限工具：可执行设备上任意命令，MCP description 中应包含安全警告。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix


def hdc_shell(command: str, serial: str | None = None) -> str:
    """
    在 HarmonyOS 设备上执行 shell 命令。

    ⚠️ 高权限工具：此工具完全透传命令到设备 shell，可执行任意操作（包括删除系统文件等
    破坏性操作）。在执行不可逆操作前，请先向用户确认。

    参数:
        command: 要在设备上执行的 shell 命令字符串
        serial: 目标设备序列号，多设备时必须指定

    返回:
        命令执行输出字符串
    """
    # 校验 command 参数不能为空
    if not command or not command.strip():
        return "[错误] command 参数不能为空"

    # 拼接命令参数：可选序列号前缀 + shell + 命令
    args = serial_prefix(serial) + ["shell", command]
    return format_result(run(args))
