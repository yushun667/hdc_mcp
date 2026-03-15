# src/hdc_mcp/config.py
"""
跨平台配置模块。
负责检测运行平台、按优先级查找 hdc 可执行文件路径、读取环境变量配置。

路径查找优先级（从高到低）：
  1. 环境变量 HDC_PATH（用户显式指定）
  2. 平台默认安装路径（DevEco Studio 安装目录）
  3. 系统 PATH（兜底）
"""
import glob
import os
import platform
import shutil


def get_hdc_path() -> str | None:
    """
    按优先级查找 hdc 可执行文件路径。

    返回:
        找到时返回绝对路径字符串，找不到时返回 None。
    """
    # 优先级 1：环境变量 HDC_PATH
    env_path = os.environ.get("HDC_PATH")
    if env_path:
        return env_path

    # 优先级 2：平台默认安装路径
    system = platform.system()
    default_paths = _get_default_paths(system)
    for pattern in default_paths:
        matches = glob.glob(os.path.expanduser(pattern))
        if matches:
            return sorted(matches)[-1]  # 取最新版本（字典序最大）

    # 优先级 3：系统 PATH 兜底
    exe_name = "hdc.exe" if system == "Windows" else "hdc"
    return shutil.which(exe_name)


def _get_default_paths(system: str) -> list[str]:
    """
    返回指定平台的 hdc 默认安装路径 glob 模式列表。

    参数:
        system: platform.system() 返回值，如 'Darwin'/'Windows'/'Linux'

    返回:
        glob 模式字符串列表，按优先级排列。
    """
    if system == "Darwin":
        return [
            "~/Library/HuaweiDevEcoStudio/sdk/*/toolchains/hdc",
            "~/Library/Application Support/HuaweiDevEcoStudio/sdk/*/toolchains/hdc",
        ]
    elif system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        return [
            os.path.join(local_app_data, "Huawei", "DevEco Studio", "sdk", "*", "toolchains", "hdc.exe"),
        ]
    elif system == "Linux":
        return [
            "~/.devecostudio/sdk/*/toolchains/hdc",
        ]
    return []


def get_timeout() -> int:
    """
    读取命令执行超时配置。

    返回:
        超时秒数，默认 30。通过环境变量 HDC_TIMEOUT 覆盖。
    """
    return int(os.environ.get("HDC_TIMEOUT", "30"))
