# src/hdc_mcp/tools/log.py
"""
日志工具模块。
封装 hdc hilog 相关命令，支持日志抓取、缓冲区管理、落盘控制、隐私/内核日志开关，
共 8 个 MCP 工具。日志抓取工具（hdc_hilog）支持全量过滤参数。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix

# 有效的日志级别集合，用于输入校验
_VALID_LEVELS = {"DEBUG", "INFO", "WARN", "ERROR", "FATAL"}

# 默认最大输出行数，防止日志无限输出
_DEFAULT_LINES = 200


def hdc_hilog(
    serial: str | None = None,
    tag: str | None = None,
    domain: str | None = None,
    level: str | None = None,
    pid: int | None = None,
    regex: str | None = None,
    head: int | None = None,
    tail: int | None = None,
    lines: int | None = None,
    timeout: int | None = None,
) -> str:
    """
    抓取设备 hilog 日志，支持全量过滤参数。
    lines 与 timeout 至少提供一个；都未提供时默认使用 lines=200 防止无限输出。

    参数:
        serial: 目标设备序列号
        tag: 按日志 tag 过滤（对应 -t）
        domain: 按 domain 过滤（对应 -D）
        level: 日志级别过滤，可选值：DEBUG/INFO/WARN/ERROR/FATAL（对应 -l）
        pid: 按进程 ID 过滤（对应 -P）
        regex: 正则表达式过滤（对应 -e）
        head: 只取前 N 条（对应 --head）
        tail: 只取后 N 条（对应 --tail）
        lines: 最大输出行数（对应 -n）
        timeout: 抓取超时秒数，传给 executor

    返回:
        日志内容字符串
    """
    # 校验 level 参数
    if level is not None and level.upper() not in _VALID_LEVELS:
        return f"[错误] level 参数无效：{level!r}，可选值：{', '.join(sorted(_VALID_LEVELS))}"

    # 默认行数限制：lines 未设置且 timeout 也未设置时，使用 _DEFAULT_LINES 防止无限输出
    effective_lines = lines if lines is not None else (_DEFAULT_LINES if timeout is None else None)

    args = serial_prefix(serial) + ["hilog"]

    if tag:
        args += ["-t", tag]
    if domain:
        args += ["-D", domain]
    if level:
        args += ["-l", level.upper()]
    if pid is not None:
        args += ["-P", str(pid)]
    if regex:
        args += ["-e", regex]
    if head is not None:
        args += ["--head", str(head)]
    if tail is not None:
        args += ["--tail", str(tail)]
    if effective_lines is not None:
        args += ["-n", str(effective_lines)]

    return format_result(run(args, timeout=timeout))


def hdc_hilog_clear(serial: str | None = None) -> str:
    """
    清除设备日志缓冲区。

    参数:
        serial: 目标设备序列号

    返回:
        操作结果字符串
    """
    return format_result(run(serial_prefix(serial) + ["hilog", "-r"]))


def hdc_hilog_buffer_info(serial: str | None = None) -> str:
    """
    查看设备日志缓冲区大小信息。

    参数:
        serial: 目标设备序列号

    返回:
        缓冲区信息字符串
    """
    return format_result(run(serial_prefix(serial) + ["hilog", "-g"]))


def hdc_hilog_write_start(serial: str | None = None) -> str:
    """
    开启日志落盘写入（将日志持久化到设备文件系统）。

    参数:
        serial: 目标设备序列号

    返回:
        操作结果字符串
    """
    return format_result(run(serial_prefix(serial) + ["hilog", "-w", "start"]))


def hdc_hilog_write_stop(serial: str | None = None) -> str:
    """
    停止日志落盘写入。

    参数:
        serial: 目标设备序列号

    返回:
        操作结果字符串
    """
    return format_result(run(serial_prefix(serial) + ["hilog", "-w", "stop"]))


def hdc_hilog_write_query(serial: str | None = None) -> str:
    """
    查询日志落盘状态。

    参数:
        serial: 目标设备序列号

    返回:
        落盘状态信息字符串
    """
    return format_result(run(serial_prefix(serial) + ["hilog", "-w", "query"]))


def hdc_hilog_privacy(enable: bool, serial: str | None = None) -> str:
    """
    开启或关闭隐私日志输出。

    参数:
        enable: True 开启，False 关闭
        serial: 目标设备序列号

    返回:
        操作结果字符串
    """
    flag = "on" if enable else "off"
    return format_result(run(serial_prefix(serial) + ["hilog", "-p", flag]))


def hdc_hilog_kernel(enable: bool, serial: str | None = None) -> str:
    """
    开启或关闭内核日志落盘。

    参数:
        enable: True 开启，False 关闭
        serial: 目标设备序列号

    返回:
        操作结果字符串
    """
    flag = "on" if enable else "off"
    return format_result(run(serial_prefix(serial) + ["hilog", "-k", flag]))
