# hdc-mcp Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 HarmonyOS hdc 工具封装为 MCP 服务，发布到 PyPI，支持 `uvx hdc-mcp` 一键运行。

**Architecture:** 分层架构：`config.py` 负责跨平台路径解析，`executor.py` 统一封装子进程调用，`tools/` 下各模块实现具体 MCP 工具，`server.py` 汇总注册并启动服务。

**Tech Stack:** Python 3.10+, mcp[cli], hatchling, pytest, pytest-mock

---

## Chunk 1: 项目基础脚手架

### Task 1: 初始化项目结构与 pyproject.toml

**Files:**
- Create: `pyproject.toml`
- Create: `src/hdc_mcp/__init__.py`
- Create: `src/hdc_mcp/server.py`
- Create: `README.md`

- [ ] **Step 1: 创建 pyproject.toml**

```toml
[project]
name = "hdc-mcp"
version = "0.1.0"
description = "MCP server for HarmonyOS hdc (HarmonyOS Device Connector) tool"
readme = "README.md"
license = { text = "MIT" }
authors = [{ name = "Your Name", email = "your@email.com" }]
requires-python = ">=3.10"
dependencies = ["mcp[cli]"]
keywords = ["mcp", "hdc", "harmonyos", "openharmony", "devtools"]
classifiers = [
    "Programming Language :: Python :: 3",
    "Operating System :: OS Independent",
    "Topic :: Software Development :: Debuggers",
]

[project.scripts]
hdc-mcp = "hdc_mcp.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/hdc_mcp"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 2: 创建目录结构**

```bash
mkdir -p src/hdc_mcp/tools
mkdir -p tests/tools
touch src/hdc_mcp/__init__.py
touch src/hdc_mcp/tools/__init__.py
touch tests/__init__.py
touch tests/tools/__init__.py
```

- [ ] **Step 3: 创建最小 server.py（占位，后续填充）**

```python
# src/hdc_mcp/server.py
"""
MCP 服务入口模块。
负责创建 FastMCP 实例，从各 tools 模块导入并注册所有工具，启动服务。
"""
from mcp.server.fastmcp import FastMCP

# 创建全局 MCP 服务实例
mcp = FastMCP("hdc-mcp")


def main() -> None:
    """MCP 服务主入口，供 uvx/命令行调用。"""
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 创建最小 README.md**

```markdown
# hdc-mcp

HarmonyOS hdc 工具的 MCP 服务，让 AI 助手直接操控鸿蒙设备。

## 快速开始

```json
{
  "mcpServers": {
    "hdc": {
      "command": "uvx",
      "args": ["hdc-mcp"]
    }
  }
}
```

## 环境变量

- `HDC_PATH`：自定义 hdc 路径（找不到 hdc 时设置）
- `HDC_TIMEOUT`：命令超时秒数（默认 30）
```

- [ ] **Step 5: 安装依赖并验证项目可启动**

```bash
uv sync
uv run hdc-mcp --help
```

期望输出：显示 MCP 帮助信息，无报错。

- [ ] **Step 6: 提交**

```bash
git add pyproject.toml src/ tests/ README.md
git commit -m "feat: 初始化 hdc-mcp 项目结构"
```

---

## Chunk 2: 核心基础模块

### Task 2: 实现 config.py（跨平台路径解析）

**Files:**
- Create: `src/hdc_mcp/config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/test_config.py
"""
config 模块测试：验证跨平台 hdc 路径解析逻辑和环境变量配置。
"""
import os
import platform
from unittest.mock import patch, MagicMock
import pytest
from hdc_mcp.config import get_hdc_path, get_timeout


class TestGetHdcPath:
    """测试 hdc 可执行文件路径解析逻辑。"""

    def test_env_var_takes_highest_priority(self, tmp_path):
        """HDC_PATH 环境变量优先级最高，即使该路径存在也应直接返回。"""
        fake_hdc = tmp_path / "hdc"
        fake_hdc.touch()
        with patch.dict(os.environ, {"HDC_PATH": str(fake_hdc)}):
            assert get_hdc_path() == str(fake_hdc)

    def test_env_var_not_set_falls_back_to_platform(self, tmp_path):
        """未设置 HDC_PATH 时，回退到 macOS 平台默认路径。"""
        fake_hdc = tmp_path / "hdc"
        fake_hdc.touch()
        with patch.dict(os.environ, {}, clear=True):
            with patch("platform.system", return_value="Darwin"):
                with patch("glob.glob", return_value=[str(fake_hdc)]):
                    result = get_hdc_path()
                    assert result == str(fake_hdc)

    def test_returns_none_when_hdc_not_found(self):
        """找不到 hdc 时返回 None。"""
        with patch.dict(os.environ, {}, clear=True):
            with patch("shutil.which", return_value=None):
                with patch("glob.glob", return_value=[]):
                    assert get_hdc_path() is None


class TestGetTimeout:
    """测试超时配置读取。"""

    def test_default_timeout(self):
        """未设置 HDC_TIMEOUT 时返回默认值 30。"""
        with patch.dict(os.environ, {}, clear=True):
            assert get_timeout() == 30

    def test_custom_timeout_from_env(self):
        """HDC_TIMEOUT 环境变量覆盖默认值。"""
        with patch.dict(os.environ, {"HDC_TIMEOUT": "60"}):
            assert get_timeout() == 60
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_config.py -v
```

期望：`ImportError` 或 `ModuleNotFoundError`，因为 `config.py` 尚不存在。

- [ ] **Step 3: 实现 config.py**

```python
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
from pathlib import Path


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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_config.py -v
```

期望：所有测试 PASS。

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/config.py tests/test_config.py
git commit -m "feat: 实现 config.py 跨平台 hdc 路径解析"
```

---

### Task 3: 实现 executor.py（命令执行器）

**Files:**
- Create: `src/hdc_mcp/executor.py`
- Create: `tests/test_executor.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/test_executor.py
"""
executor 模块测试：验证 hdc 命令执行、超时处理、错误捕获。
"""
import subprocess
from unittest.mock import patch, MagicMock
import pytest
from hdc_mcp.executor import run, ExecuteResult


class TestExecuteResult:
    """测试 ExecuteResult 数据结构。"""

    def test_default_timed_out_is_false(self):
        """timed_out 默认值为 False。"""
        result = ExecuteResult(stdout="ok", stderr="", returncode=0)
        assert result.timed_out is False

    def test_fields(self):
        """所有字段可正确赋值。"""
        result = ExecuteResult(stdout="out", stderr="err", returncode=1, timed_out=True)
        assert result.stdout == "out"
        assert result.stderr == "err"
        assert result.returncode == 1
        assert result.timed_out is True


class TestRun:
    """测试 run() 函数的各种场景。"""

    def test_successful_command(self):
        """正常命令执行返回 stdout 内容。"""
        mock_result = MagicMock()
        mock_result.stdout = "device_list\n"
        mock_result.stderr = ""
        mock_result.returncode = 0

        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", return_value=mock_result):
                result = run(["list", "targets"])

        assert result.stdout == "device_list\n"
        assert result.returncode == 0
        assert result.timed_out is False

    def test_hdc_not_found_returns_error(self):
        """hdc 未找到时返回描述性错误信息。"""
        with patch("hdc_mcp.executor.get_hdc_path", return_value=None):
            result = run(["list", "targets"])

        assert result.returncode == -1
        assert "HDC_PATH" in result.stderr
        assert result.timed_out is False

    def test_timeout_returns_timed_out_flag(self):
        """命令超时时 timed_out=True，returncode=-1。"""
        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired(cmd="hdc", timeout=30)):
                result = run(["shell", "sleep 100"], timeout=1)

        assert result.timed_out is True
        assert result.returncode == -1

    def test_command_failure_returns_stderr(self):
        """命令失败时返回 stderr 内容和非零 returncode。"""
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_result.stderr = "[Fail] Connect failed"
        mock_result.returncode = 1

        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", return_value=mock_result):
                result = run(["tconn", "192.168.1.1:5555"])

        assert result.returncode == 1
        assert "Connect failed" in result.stderr

    def test_uses_custom_timeout(self):
        """run() 使用传入的 timeout 参数。"""
        mock_result = MagicMock(stdout="", stderr="", returncode=0)

        with patch("hdc_mcp.executor.get_hdc_path", return_value="/usr/bin/hdc"):
            with patch("subprocess.run", return_value=mock_result) as mock_subprocess:
                run(["list", "targets"], timeout=10)
                _, kwargs = mock_subprocess.call_args
                assert kwargs["timeout"] == 10
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_executor.py -v
```

期望：`ImportError`，因为 `executor.py` 尚不存在。

- [ ] **Step 3: 实现 executor.py**

```python
# src/hdc_mcp/executor.py
"""
hdc 命令执行器模块。
统一封装 hdc 子进程调用，处理超时、错误捕获和输出解析。
不使用 shell=True，避免命令注入风险。
"""
import subprocess
from dataclasses import dataclass, field

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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/test_executor.py -v
```

期望：所有测试 PASS。

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/executor.py tests/test_executor.py
git commit -m "feat: 实现 executor.py hdc 命令执行器"
```

---

## Chunk 3: 设备管理与文件传输工具

### Task 4: 提取公共工具函数（_utils.py）

**Files:**
- Create: `src/hdc_mcp/tools/_utils.py`

- [ ] **Step 1: 创建 `_utils.py`，提取 `_format_result` 公共函数**

```python
# src/hdc_mcp/tools/_utils.py
"""
工具模块公共工具函数。
避免各工具模块重复定义相同的辅助函数。
"""
from hdc_mcp.executor import ExecuteResult


def format_result(result: ExecuteResult) -> str:
    """
    将 ExecuteResult 格式化为工具返回字符串。

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
    返回设备序列号前缀参数列表。

    参数:
        serial: 设备序列号，None 时返回空列表

    返回:
        ["-t", serial] 或 []
    """
    return ["-t", serial] if serial else []
```

- [ ] **Step 2: 提交**

```bash
git add src/hdc_mcp/tools/_utils.py
git commit -m "feat: 提取工具模块公共函数到 _utils.py"
```

---

### Task 5: 实现设备管理工具（device.py）

**Files:**
- Create: `src/hdc_mcp/tools/device.py`
- Create: `tests/tools/test_device.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/tools/test_device.py
"""
设备管理工具测试：验证各工具正确构建 hdc 命令参数。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.device import (
    hdc_list_targets, hdc_target_connect, hdc_target_disconnect,
    hdc_target_reboot, hdc_target_mode, hdc_smode,
)

# 成功结果的 mock 工厂
def ok(stdout=""):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcListTargets:
    def test_basic_call(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok("SN001\tUSB")) as mock_run:
            result = hdc_list_targets(verbose=False)
            mock_run.assert_called_once_with(["list", "targets"])
            assert "SN001" in result

    def test_verbose_flag(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_list_targets(verbose=True)
            mock_run.assert_called_once_with(["list", "targets", "-v"])


class TestHdcTargetConnect:
    def test_connect_address(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok("Connect OK")) as mock_run:
            result = hdc_target_connect(address="192.168.1.100:5555")
            mock_run.assert_called_once_with(["tconn", "192.168.1.100:5555"])
            assert "Connect OK" in result


class TestHdcTargetDisconnect:
    def test_disconnect_with_address(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_disconnect(address="192.168.1.100:5555")
            mock_run.assert_called_once_with(["tdisconn", "192.168.1.100:5555"])

    def test_disconnect_all(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_disconnect(address=None)
            mock_run.assert_called_once_with(["tdisconn"])


class TestHdcTargetReboot:
    def test_reboot_with_serial(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_reboot(serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "target", "boot"])


class TestHdcTargetMode:
    def test_usb_mode(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_mode(mode="usb")
            mock_run.assert_called_once_with(["tmode", "usb"])

    def test_tcp_mode(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_target_mode(mode="tcp")
            mock_run.assert_called_once_with(["tmode", "tcp"])

    def test_invalid_mode_raises(self):
        result = hdc_target_mode(mode="invalid")
        assert "错误" in result or "invalid" in result


class TestHdcSmode:
    def test_smode_basic(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_smode(reset=False)
            mock_run.assert_called_once_with(["smode"])

    def test_smode_reset(self):
        with patch("hdc_mcp.tools.device.run", return_value=ok()) as mock_run:
            hdc_smode(reset=True)
            mock_run.assert_called_once_with(["smode", "-r"])
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/tools/test_device.py -v
```

- [ ] **Step 3: 实现 device.py**

```python
# src/hdc_mcp/tools/device.py
"""
设备管理工具模块。
封装 hdc 设备连接、断开、重启、模式切换等操作，共 6 个 MCP 工具。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix


def _fmt(result) -> str:
    return format_result(result)


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
    return _fmt(run(args))


def hdc_target_connect(address: str) -> str:
    """
    通过 TCP/IP 连接网络设备。

    参数:
        address: 设备地址，格式为 host:port，如 192.168.1.100:5555

    返回:
        连接结果字符串
    """
    return _fmt(run(["tconn", address]))


def hdc_target_disconnect(address: str | None = None) -> str:
    """
    断开网络设备连接。

    参数:
        address: 设备地址（host:port），None 时断开所有网络设备

    返回:
        断开结果字符串
    """
    args = ["tdisconn"]
    if address:
        args.append(address)
    return _fmt(run(args))


def hdc_target_reboot(serial: str) -> str:
    """
    重启指定设备。

    参数:
        serial: 设备序列号（可通过 hdc_list_targets 获取）

    返回:
        重启结果字符串
    """
    return _fmt(run(["-t", serial, "target", "boot"]))


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
    return _fmt(run(["tmode", mode]))


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
    return _fmt(run(args))
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/tools/test_device.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/tools/device.py tests/tools/test_device.py
git commit -m "feat: 实现设备管理工具 device.py（6个工具）"
```

---

### Task 5: 实现文件传输工具（file.py）

**Files:**
- Create: `src/hdc_mcp/tools/file.py`
- Create: `tests/tools/test_file.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/tools/test_file.py
"""
文件传输工具测试：验证 file send/recv 命令参数构建。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.file import hdc_file_send, hdc_file_recv

def ok(stdout="[成功]"):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcFileSend:
    def test_basic_send(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_send(local="/tmp/app.hap", remote="/data/local/tmp/app.hap")
            mock_run.assert_called_once_with(["file", "send", "/tmp/app.hap", "/data/local/tmp/app.hap"])

    def test_send_with_serial(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_send(local="/tmp/app.hap", remote="/data/local/tmp/app.hap", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "file", "send", "/tmp/app.hap", "/data/local/tmp/app.hap"])


class TestHdcFileRecv:
    def test_basic_recv(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_recv(remote="/data/local/tmp/log.txt", local="/tmp/log.txt")
            mock_run.assert_called_once_with(["file", "recv", "/data/local/tmp/log.txt", "/tmp/log.txt"])

    def test_recv_with_serial(self):
        with patch("hdc_mcp.tools.file.run", return_value=ok()) as mock_run:
            hdc_file_recv(remote="/data/local/tmp/log.txt", local="/tmp/log.txt", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "file", "recv", "/data/local/tmp/log.txt", "/tmp/log.txt"])
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/tools/test_file.py -v
```

- [ ] **Step 3: 实现 file.py**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/tools/test_file.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/tools/file.py tests/tools/test_file.py
git commit -m "feat: 实现文件传输工具 file.py（2个工具）"
```

---

## Chunk 4: 应用管理与 Shell 工具

### Task 6: 实现应用管理工具（app.py）

**Files:**
- Create: `src/hdc_mcp/tools/app.py`
- Create: `tests/tools/test_app.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/tools/test_app.py
"""
应用管理工具测试：验证 app install/uninstall 命令参数构建。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.app import hdc_app_install, hdc_app_uninstall

def ok(stdout="[成功]"):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcAppInstall:
    def test_basic_install(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap")
            mock_run.assert_called_once_with(["app", "install", "/tmp/app.hap"])

    def test_install_with_replace(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap", replace=True)
            mock_run.assert_called_once_with(["app", "install", "-r", "/tmp/app.hap"])

    def test_install_with_shared(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap", shared=True)
            mock_run.assert_called_once_with(["app", "install", "-s", "/tmp/app.hap"])

    def test_install_with_serial(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_install(hap_path="/tmp/app.hap", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "app", "install", "/tmp/app.hap"])


class TestHdcAppUninstall:
    def test_basic_uninstall(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_uninstall(bundle_name="com.example.app")
            mock_run.assert_called_once_with(["app", "uninstall", "com.example.app"])

    def test_uninstall_shared(self):
        with patch("hdc_mcp.tools.app.run", return_value=ok()) as mock_run:
            hdc_app_uninstall(bundle_name="com.example.app", shared=True)
            mock_run.assert_called_once_with(["app", "uninstall", "-s", "com.example.app"])
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/tools/test_app.py -v
```

- [ ] **Step 3: 实现 app.py**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/tools/test_app.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/tools/app.py tests/tools/test_app.py
git commit -m "feat: 实现应用管理工具 app.py（2个工具）"
```

---

### Task 7: 实现 Shell 工具（shell.py）

**Files:**
- Create: `src/hdc_mcp/tools/shell.py`
- Create: `tests/tools/test_shell.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/tools/test_shell.py
"""
Shell 工具测试：验证 shell 命令透传和高权限工具描述。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.shell import hdc_shell

def ok(stdout=""):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcShell:
    def test_basic_shell_command(self):
        with patch("hdc_mcp.tools.shell.run", return_value=ok("total 0")) as mock_run:
            result = hdc_shell(command="ls /data")
            mock_run.assert_called_once_with(["shell", "ls /data"])
            assert "total 0" in result

    def test_shell_with_serial(self):
        with patch("hdc_mcp.tools.shell.run", return_value=ok()) as mock_run:
            hdc_shell(command="ls", serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "shell", "ls"])

    def test_empty_command_returns_error(self):
        result = hdc_shell(command="")
        assert "错误" in result
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/tools/test_shell.py -v
```

- [ ] **Step 3: 实现 shell.py**

```python
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
    if not command or not command.strip():
        return "[错误] command 参数不能为空"

    args = serial_prefix(serial) + ["shell", command]
    return format_result(run(args))
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/tools/test_shell.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/tools/shell.py tests/tools/test_shell.py
git commit -m "feat: 实现 Shell 工具 shell.py（1个工具）"
```

---

## Chunk 5: 日志工具

### Task 8: 实现日志工具（log.py）

**Files:**
- Create: `src/hdc_mcp/tools/log.py`
- Create: `tests/tools/test_log.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/tools/test_log.py
"""
日志工具测试：验证 hilog 命令的全量过滤参数构建和约束校验。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.log import (
    hdc_hilog, hdc_hilog_clear, hdc_hilog_buffer_info,
    hdc_hilog_write_start, hdc_hilog_write_stop, hdc_hilog_write_query,
    hdc_hilog_privacy, hdc_hilog_kernel,
)
import pytest

def ok(stdout="log output"):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcHilog:
    def test_requires_lines_or_timeout(self):
        """lines 和 timeout 都未提供时，使用默认 lines=200。"""
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog()
            args = mock_run.call_args[0][0]
            assert "-n" in args or "--head" in args  # 默认限制行数

    def test_filter_by_level(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(level="ERROR", lines=50)
            args = mock_run.call_args[0][0]
            assert "-l" in args
            assert "ERROR" in args

    def test_filter_by_tag(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(tag="MyApp", lines=50)
            args = mock_run.call_args[0][0]
            assert "-t" in args
            assert "MyApp" in args

    def test_filter_by_pid(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(pid=1234, lines=50)
            args = mock_run.call_args[0][0]
            assert "-P" in args
            assert "1234" in args

    def test_invalid_level_returns_error(self):
        result = hdc_hilog(level="VERBOSE", lines=50)
        assert "错误" in result

    def test_with_serial(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog(serial="SN001", lines=10)
            args = mock_run.call_args[0][0]
            # serial 的 -t 必须在 hilog 之前
            t_index = args.index("-t")
            hilog_index = args.index("hilog")
            assert t_index < hilog_index
            assert args[t_index + 1] == "SN001"


class TestHdcHilogClear:
    def test_clear(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_clear()
            mock_run.assert_called_once_with(["hilog", "-r"])


class TestHdcHilogBufferInfo:
    def test_buffer_info(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_buffer_info()
            mock_run.assert_called_once_with(["hilog", "-g"])


class TestHdcHilogWrite:
    def test_write_start(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_write_start()
            mock_run.assert_called_once_with(["hilog", "-w", "start"])

    def test_write_stop(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_write_stop()
            mock_run.assert_called_once_with(["hilog", "-w", "stop"])

    def test_write_query(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_write_query()
            mock_run.assert_called_once_with(["hilog", "-w", "query"])


class TestHdcHilogPrivacy:
    def test_enable_privacy(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_privacy(enable=True)
            mock_run.assert_called_once_with(["hilog", "-p", "on"])

    def test_disable_privacy(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_privacy(enable=False)
            mock_run.assert_called_once_with(["hilog", "-p", "off"])


class TestHdcHilogKernel:
    def test_enable_kernel(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_kernel(enable=True)
            mock_run.assert_called_once_with(["hilog", "-k", "on"])

    def test_disable_kernel(self):
        with patch("hdc_mcp.tools.log.run", return_value=ok()) as mock_run:
            hdc_hilog_kernel(enable=False)
            mock_run.assert_called_once_with(["hilog", "-k", "off"])
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/tools/test_log.py -v
```

- [ ] **Step 3: 实现 log.py**

```python
# src/hdc_mcp/tools/log.py
"""
日志工具模块。
封装 hdc hilog 相关命令，支持日志抓取、缓冲区管理、落盘控制、隐私/内核日志开关，
共 8 个 MCP 工具。日志抓取工具（hdc_hilog）支持全量过滤参数。
"""
from hdc_mcp.executor import run
from hdc_mcp.tools._utils import format_result, serial_prefix


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

    # 默认行数限制
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/tools/test_log.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/tools/log.py tests/tools/test_log.py
git commit -m "feat: 实现日志工具 log.py（8个工具）"
```

---

## Chunk 6: 端口转发与服务管理工具

### Task 9: 实现端口转发工具（forward.py）

**Files:**
- Create: `src/hdc_mcp/tools/forward.py`
- Create: `tests/tools/test_forward.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/tools/test_forward.py
"""
端口转发工具测试：验证 fport 命令参数构建。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.forward import hdc_fport_add, hdc_fport_rm, hdc_fport_list

def ok(stdout=""):
    return ExecuteResult(stdout=stdout, stderr="", returncode=0)


class TestHdcFportAdd:
    def test_add_port_forward(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok()) as mock_run:
            hdc_fport_add(local_port=8080, remote_port=8080)
            mock_run.assert_called_once_with(["fport", "tcp:8080", "tcp:8080"])

    def test_add_with_serial(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok()) as mock_run:
            hdc_fport_add(local_port=8080, remote_port=9090, serial="SN001")
            mock_run.assert_called_once_with(["-t", "SN001", "fport", "tcp:8080", "tcp:9090"])


class TestHdcFportRm:
    def test_remove_port_forward(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok()) as mock_run:
            hdc_fport_rm(local_port=8080, remote_port=8080)
            mock_run.assert_called_once_with(["fport", "rm", "tcp:8080", "tcp:8080"])


class TestHdcFportList:
    def test_list_rules(self):
        with patch("hdc_mcp.tools.forward.run", return_value=ok("tcp:8080 tcp:8080")) as mock_run:
            result = hdc_fport_list()
            mock_run.assert_called_once_with(["fport", "ls"])
            assert "8080" in result
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/tools/test_forward.py -v
```

- [ ] **Step 3: 实现 forward.py**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/tools/test_forward.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/tools/forward.py tests/tools/test_forward.py
git commit -m "feat: 实现端口转发工具 forward.py（3个工具）"
```

---

### Task 10: 实现服务管理工具（server_tools.py）

**Files:**
- Create: `src/hdc_mcp/tools/server_tools.py`
- Create: `tests/tools/test_server_tools.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/tools/test_server_tools.py
"""
服务管理工具测试：验证 hdc start/kill 命令。
"""
from unittest.mock import patch
from hdc_mcp.executor import ExecuteResult
from hdc_mcp.tools.server_tools import hdc_start_server, hdc_kill_server

def ok():
    return ExecuteResult(stdout="", stderr="", returncode=0)


class TestHdcStartServer:
    def test_start(self):
        with patch("hdc_mcp.tools.server_tools.run", return_value=ok()) as mock_run:
            hdc_start_server()
            mock_run.assert_called_once_with(["start"])


class TestHdcKillServer:
    def test_kill(self):
        with patch("hdc_mcp.tools.server_tools.run", return_value=ok()) as mock_run:
            hdc_kill_server()
            mock_run.assert_called_once_with(["kill"])
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/tools/test_server_tools.py -v
```

- [ ] **Step 3: 实现 server_tools.py**

```python
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
uv run pytest tests/tools/test_server_tools.py -v
```

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/tools/server_tools.py tests/tools/test_server_tools.py
git commit -m "feat: 实现服务管理工具 server_tools.py（2个工具）"
```

---

## Chunk 7: MCP 注册与最终集成

### Task 11: 在 server.py 注册所有 MCP 工具

**Files:**
- Modify: `src/hdc_mcp/server.py`
- Create: `tests/test_server.py`

- [ ] **Step 1: 编写失败测试**

```python
# tests/test_server.py
"""
server 模块测试：验证所有工具已注册到 MCP 实例。
"""
from hdc_mcp.server import mcp


class TestMcpToolsRegistered:
    """验证所有 24 个工具都已注册到 MCP 实例。"""

    def _get_tool_names(self):
        # FastMCP 将工具存储在内部字典中
        return list(mcp._tool_manager._tools.keys())

    def test_device_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_list_targets", "hdc_target_connect", "hdc_target_disconnect",
                     "hdc_target_reboot", "hdc_target_mode", "hdc_smode"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_file_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_file_send", "hdc_file_recv"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_app_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_app_install", "hdc_app_uninstall"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_shell_tools_registered(self):
        names = self._get_tool_names()
        assert "hdc_shell" in names

    def test_log_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_hilog", "hdc_hilog_clear", "hdc_hilog_buffer_info",
                     "hdc_hilog_write_start", "hdc_hilog_write_stop", "hdc_hilog_write_query",
                     "hdc_hilog_privacy", "hdc_hilog_kernel"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_forward_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_fport_add", "hdc_fport_rm", "hdc_fport_list"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_server_tools_registered(self):
        names = self._get_tool_names()
        for tool in ["hdc_start_server", "hdc_kill_server"]:
            assert tool in names, f"工具 {tool} 未注册"

    def test_total_tool_count(self):
        names = self._get_tool_names()
        assert len(names) == 24, f"预期 24 个工具，实际 {len(names)} 个：{names}"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
uv run pytest tests/test_server.py -v
```

- [ ] **Step 3: 更新 server.py 注册所有工具**

```python
# src/hdc_mcp/server.py
"""
MCP 服务入口模块。
负责创建 FastMCP 实例，从各 tools 模块导入并注册所有工具，启动服务。
工具按功能分模块组织，共 24 个 MCP 工具。
"""
from mcp.server.fastmcp import FastMCP

from hdc_mcp.tools.device import (
    hdc_list_targets,
    hdc_target_connect,
    hdc_target_disconnect,
    hdc_target_reboot,
    hdc_target_mode,
    hdc_smode,
)
from hdc_mcp.tools.file import hdc_file_send, hdc_file_recv
from hdc_mcp.tools.app import hdc_app_install, hdc_app_uninstall
from hdc_mcp.tools.shell import hdc_shell
from hdc_mcp.tools.log import (
    hdc_hilog,
    hdc_hilog_clear,
    hdc_hilog_buffer_info,
    hdc_hilog_write_start,
    hdc_hilog_write_stop,
    hdc_hilog_write_query,
    hdc_hilog_privacy,
    hdc_hilog_kernel,
)
from hdc_mcp.tools.forward import hdc_fport_add, hdc_fport_rm, hdc_fport_list
from hdc_mcp.tools.server_tools import hdc_start_server, hdc_kill_server

# 创建全局 MCP 服务实例
mcp = FastMCP("hdc-mcp")

# 注册所有工具到 MCP 实例
# 设备管理（6个）
mcp.tool()(hdc_list_targets)
mcp.tool()(hdc_target_connect)
mcp.tool()(hdc_target_disconnect)
mcp.tool()(hdc_target_reboot)
mcp.tool()(hdc_target_mode)
mcp.tool()(hdc_smode)

# 文件传输（2个）
mcp.tool()(hdc_file_send)
mcp.tool()(hdc_file_recv)

# 应用管理（2个）
mcp.tool()(hdc_app_install)
mcp.tool()(hdc_app_uninstall)

# Shell 命令（1个，高权限工具）
mcp.tool()(hdc_shell)

# 日志（8个）
mcp.tool()(hdc_hilog)
mcp.tool()(hdc_hilog_clear)
mcp.tool()(hdc_hilog_buffer_info)
mcp.tool()(hdc_hilog_write_start)
mcp.tool()(hdc_hilog_write_stop)
mcp.tool()(hdc_hilog_write_query)
mcp.tool()(hdc_hilog_privacy)
mcp.tool()(hdc_hilog_kernel)

# 端口转发（3个）
mcp.tool()(hdc_fport_add)
mcp.tool()(hdc_fport_rm)
mcp.tool()(hdc_fport_list)

# 服务管理（2个）
mcp.tool()(hdc_start_server)
mcp.tool()(hdc_kill_server)


def main() -> None:
    """MCP 服务主入口，供 uvx/命令行调用。"""
    mcp.run()


if __name__ == "__main__":
    main()
```

- [ ] **Step 4: 运行全量测试**

```bash
uv run pytest -v
```

期望：所有测试 PASS，无警告。

- [ ] **Step 5: 提交**

```bash
git add src/hdc_mcp/server.py tests/test_server.py
git commit -m "feat: server.py 注册全部 24 个 MCP 工具，完成集成"
```

---

## Chunk 8: README 与发布验证

### Task 12: 编写 README 并验证发布

**Files:**
- Modify: `README.md`

- [ ] **Step 1: 编写 README.md**

内容包含：项目简介、安装方式（`uvx hdc-mcp`）、Claude Desktop 配置示例、支持平台、工具清单（24个工具分类列表）、环境变量说明（`HDC_PATH`、`HDC_TIMEOUT`）。

```markdown
# hdc-mcp

HarmonyOS hdc 工具的 MCP（Model Context Protocol）服务，让 AI 助手直接操控鸿蒙设备。

## 快速开始

### 安装（通过 uvx，无需手动安装依赖）

在 Claude Desktop / Cursor 等 MCP 客户端配置文件中添加：

```json
{
  "mcpServers": {
    "hdc": {
      "command": "uvx",
      "args": ["hdc-mcp"],
      "env": {
        "HDC_PATH": "/path/to/hdc"  // 可选，找不到 hdc 时手动指定
      }
    }
  }
}
```

## 前置条件

- 已安装 [DevEco Studio](https://developer.huawei.com/consumer/cn/deveco-studio/)（包含 hdc 工具）
- Python 3.10+（由 uvx 自动管理）
- [uv](https://docs.astral.sh/uv/) 工具（用于 uvx）

## 支持平台

| 平台 | hdc 自动探测 | 手动配置（HDC_PATH） |
|------|------------|-------------------|
| macOS | ✅ 自动 | ✅ 支持 |
| Windows | ✅ 自动 | ✅ 支持 |
| Linux | ❌ 需手动配置 | ✅ 支持 |

## 工具清单（24 个）

### 设备管理
- `hdc_list_targets` — 列出已连接设备
- `hdc_target_connect` — 连接网络设备（TCP/IP）
- `hdc_target_disconnect` — 断开网络设备
- `hdc_target_reboot` — 重启设备
- `hdc_target_mode` — 切换连接模式（usb/tcp）
- `hdc_smode` — 切换服务器权限模式

### 文件传输
- `hdc_file_send` — 推送文件到设备
- `hdc_file_recv` — 从设备拉取文件

### 应用管理
- `hdc_app_install` — 安装 HAP 包
- `hdc_app_uninstall` — 卸载应用

### Shell 命令
- `hdc_shell` ⚠️ — 执行设备 shell 命令（高权限）

### 日志（hilog）
- `hdc_hilog` — 抓取日志（支持 tag/domain/level/pid/regex 过滤）
- `hdc_hilog_clear` — 清除日志缓冲区
- `hdc_hilog_buffer_info` — 查看缓冲区大小
- `hdc_hilog_write_start` — 开启日志落盘
- `hdc_hilog_write_stop` — 停止日志落盘
- `hdc_hilog_write_query` — 查询落盘状态
- `hdc_hilog_privacy` — 开启/关闭隐私日志
- `hdc_hilog_kernel` — 开启/关闭内核日志落盘

### 端口转发
- `hdc_fport_add` — 添加端口转发规则
- `hdc_fport_rm` — 删除端口转发规则
- `hdc_fport_list` — 列出端口转发规则

### 服务管理
- `hdc_start_server` — 启动 hdc 服务端
- `hdc_kill_server` — 停止 hdc 服务端

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `HDC_PATH` | 自动探测 | hdc 可执行文件绝对路径 |
| `HDC_TIMEOUT` | `30` | 命令执行超时秒数 |

## 开发

```bash
git clone <repo>
cd hdc_mcp
uv sync
uv run pytest
```
```

- [ ] **Step 2: 验证构建**

```bash
uv build
```

期望：在 `dist/` 目录生成 `.whl` 和 `.tar.gz` 文件，无错误。

- [ ] **Step 3: 验证本地安装可运行**

```bash
uvx --from dist/hdc_mcp-0.1.0-py3-none-any.whl hdc-mcp --help
```

期望：显示 MCP 服务帮助信息，无报错。

- [ ] **Step 4: 运行全量测试最终确认**

```bash
uv run pytest -v --tb=short
```

期望：全部通过。

- [ ] **Step 5: 最终提交**

```bash
git add README.md
git commit -m "docs: 添加 README，完成 hdc-mcp v0.1.0 初始实现"
```

---

## 验证清单

实现完成后，通过以下步骤端到端验证：

1. **构建验证：** `uv build` 无错误，`dist/` 目录有产物
2. **单元测试：** `uv run pytest -v` 全部通过（目标覆盖率 80%+）
3. **本地运行：** `uv run hdc-mcp` 服务启动无报错
4. **MCP 工具发现：** 使用 MCP 客户端（如 Claude Desktop）连接后，能看到 24 个工具
5. **基本功能：** 调用 `hdc_list_targets` 返回设备列表（或 hdc 未找到的提示）
6. **日志功能：** 调用 `hdc_hilog(lines=10)` 返回日志内容
