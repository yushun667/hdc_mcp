# src/hdc_mcp/executor.py
"""
hdc 命令执行器模块。
统一封装 hdc 子进程调用，处理超时、错误捕获和输出解析。
不使用 shell=True，避免命令注入风险。
"""
import subprocess
from dataclasses import dataclass

from hdc_mcp.config import get_hdc_path, get_timeout


@dataclass
class ExecuteResult:
    """
    hdc 命令执行结果。

    属性:
        stdout: 标准输出内容
        stderr: 标准错误内容
        returncode: 进程返回码，0 表示成功，-1 表示内部错误
        timed_out: 是否因超时终止，避免工具层解析字符串判断
    """
    stdout: str
    stderr: str
    returncode: int
    timed_out: bool = False


def run(args: list[str], timeout: int | None = None) -> ExecuteResult:
    """
    执行 hdc 命令。

    参数:
        args: hdc 子命令及参数列表，如 ['list', 'targets'] 或 ['-t', 'SN001', 'shell', 'ls']
        timeout: 超时秒数，None 时使用 HDC_TIMEOUT 环境变量配置（默认 30）

    返回:
        ExecuteResult 结构化结果
    """
    hdc_path = get_hdc_path()
    if hdc_path is None:
        return ExecuteResult(
            stdout="",
            stderr=(
                "找不到 hdc 可执行文件。请通过以下方式之一解决：\n"
                "1. 安装 DevEco Studio（自动包含 hdc）\n"
                "2. 设置环境变量 HDC_PATH 指向 hdc 可执行文件的绝对路径"
            ),
            returncode=-1,
        )

    effective_timeout = timeout if timeout is not None else get_timeout()
    cmd = [hdc_path] + args

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=effective_timeout,
        )
        return ExecuteResult(
            stdout=proc.stdout,
            stderr=proc.stderr,
            returncode=proc.returncode,
        )
    except subprocess.TimeoutExpired:
        return ExecuteResult(
            stdout="",
            stderr=f"命令执行超时（{effective_timeout}s）。可通过环境变量 HDC_TIMEOUT 增大超时限制。",
            returncode=-1,
            timed_out=True,
        )
    except Exception as e:
        return ExecuteResult(
            stdout="",
            stderr=f"执行 hdc 命令时发生错误：{e}",
            returncode=-1,
        )
