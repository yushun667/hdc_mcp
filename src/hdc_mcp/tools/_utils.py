# src/hdc_mcp/tools/_utils.py
"""
工具模块公共工具函数。
避免各工具模块重复定义相同的辅助函数，供所有 tools 子模块复用。
"""
from hdc_mcp.executor import ExecuteResult


def format_result(result: ExecuteResult) -> str:
    """
    将 ExecuteResult 格式化为 MCP 工具返回字符串。

    参数:
        result: ExecuteResult 实例

    返回:
        格式化后的输出字符串：超时/错误时包含错误信息，成功时返回 stdout 内容
    """
    if result.timed_out:
        return f"[超时] {result.stderr}"
    if result.returncode != 0:
        return f"[错误 {result.returncode}] {result.stderr or result.stdout}"
    return result.stdout or result.stderr or "[成功]"


def serial_prefix(serial: str | None) -> list[str]:
    """
    返回设备序列号前缀参数列表，用于多设备场景指定目标设备。

    参数:
        serial: 设备序列号，None 时返回空列表

    返回:
        ["-t", serial] 或 []
    """
    return ["-t", serial] if serial else []
