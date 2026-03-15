# hdc-mcp 设计文档

**日期：** 2026-03-15
**状态：** 已审查

---

## 1. 项目概述

### 目标

将 HarmonyOS 设备调试工具 `hdc`（HarmonyOS Device Connector）封装为 MCP（Model Context Protocol）服务，使 AI 助手能够直接操控鸿蒙设备，完成设备调试、文件传输、应用管理、日志分析等开发工作。

### 使用场景

- 个人鸿蒙应用开发者日常调试
- 通过 AI 助手（Claude Desktop / Cursor 等）自动化设备操作
- 支持 USB 连接和 TCP/IP 网络连接两种设备接入方式

### 分发方式

发布到 PyPI，通过 `uvx hdc-mcp` 一键运行，无需手动安装依赖。

---

## 2. 技术选型

| 项目 | 选择 | 说明 |
|------|------|------|
| 语言 | Python 3.10+ | 生态丰富，MCP SDK 官方支持 |
| MCP SDK | `mcp[cli]` | 官方 Python MCP SDK |
| 打包工具 | `uv` / `pyproject.toml` | 现代 Python 打包标准 |
| 分发平台 | PyPI | 通过 `uvx` 一键运行 |
| 支持平台 | Windows、macOS、Linux（需手动配置 HDC_PATH） | 跨平台，路径自动适配 |

---

## 3. 项目结构

```
hdc_mcp/
├── src/
│   └── hdc_mcp/
│       ├── __init__.py
│       ├── server.py          # MCP 服务入口，汇总并注册所有工具
│       ├── executor.py        # hdc 命令执行器，统一封装子进程调用
│       ├── config.py          # 平台检测、hdc 路径解析、环境变量配置
│       └── tools/
│           ├── __init__.py
│           ├── device.py      # 设备管理工具（6个）
│           ├── file.py        # 文件传输工具（2个）
│           ├── app.py         # 应用管理工具（2个）
│           ├── shell.py       # Shell 命令工具（1个）
│           ├── log.py         # 日志工具（8个）
│           ├── forward.py     # 端口转发工具（3个）
│           └── server_tools.py # 服务管理工具（2个）
├── docs/
│   └── superpowers/
│       └── specs/
│           └── 2026-03-15-hdc-mcp-design.md
├── pyproject.toml
└── README.md
```

---

## 4. 核心模块设计

### 4.1 config.py — 配置与路径解析

**职责：** 检测运行平台，自动查找 hdc 可执行文件路径，支持通过环境变量 `HDC_PATH` 自定义。

**hdc 路径查找优先级（从高到低）：**

1. **环境变量 `HDC_PATH`**（最高优先级）：用户显式指定，直接使用
2. **平台默认安装路径**：按平台自动探测
   - macOS：`~/Library/HuaweiDevEcoStudio/sdk/*/toolchains/hdc`
   - Windows：`%LOCALAPPDATA%\Huawei\DevEco Studio\sdk\*\toolchains\hdc.exe`
   - Linux：`~/.devecostudio/sdk/*/toolchains/hdc`（需手动配置 `HDC_PATH`，不保证自动探测）
3. **系统 PATH**（兜底）：在 `PATH` 中查找 `hdc` / `hdc.exe`

**配置项：**
```
HDC_PATH        # 自定义 hdc 可执行文件绝对路径
HDC_TIMEOUT     # 命令执行超时秒数，默认 30
```

### 4.2 executor.py — 命令执行器

**职责：** 统一封装 hdc 子进程调用，处理超时、错误捕获、输出解析。

**接口：**
```python
@dataclass
class ExecuteResult:
    stdout: str       # 标准输出内容
    stderr: str       # 标准错误内容
    returncode: int   # 进程返回码，0 表示成功
    timed_out: bool = False  # 是否因超时终止，避免工具层解析字符串判断

def run(args: list[str], timeout: int | None = None) -> ExecuteResult:
    """
    执行 hdc 命令
    args: hdc 子命令及参数列表，如 ['list', 'targets']
    返回: ExecuteResult 结构化结果
    """
```

**设计要点：**
- 不使用 `shell=True`，避免命令注入风险
- 统一捕获 `TimeoutExpired`、`FileNotFoundError`（hdc 未找到）等异常
- 返回结构化结果，工具层负责格式化输出给 AI

### 4.3 server.py — MCP 服务入口

**职责：** 创建 MCP server 实例，从各 tools 模块导入并注册所有工具，启动服务。

```python
mcp = FastMCP("hdc-mcp")
# 各模块工具注册到同一 mcp 实例
```

---

## 5. MCP 工具清单（共 24 个）

### 5.1 设备管理（device.py）— 6 个工具

| 工具名 | hdc 命令 | 参数 | 说明 |
|--------|---------|------|------|
| `hdc_list_targets` | `hdc list targets [-v]` | `verbose: bool` | 列出所有已连接设备 |
| `hdc_target_connect` | `hdc tconn <host:port>` | `address: str` | 连接网络设备（TCP/IP） |
| `hdc_target_disconnect` | `hdc tdisconn [host:port]` | `address: str?` | 断开网络设备连接 |
| `hdc_target_reboot` | `hdc -t <sn> target boot` | `serial: str` | 重启指定设备 |
| `hdc_target_mode` | `hdc tmode usb/tcp` | `mode: Literal["usb", "tcp"]` | 切换设备连接模式 |
| `hdc_smode` | `hdc smode [-r]` | `reset: bool` | 切换服务器权限模式 |

### 5.2 文件传输（file.py）— 2 个工具

| 工具名 | hdc 命令 | 参数 | 说明 |
|--------|---------|------|------|
| `hdc_file_send` | `hdc [-t sn] file send <local> <remote>` | `local: str, remote: str, serial: str?` | 推送本地文件/目录到设备 |
| `hdc_file_recv` | `hdc [-t sn] file recv <remote> <local>` | `remote: str, local: str, serial: str?` | 从设备拉取文件/目录到本地 |

### 5.3 应用管理（app.py）— 2 个工具

| 工具名 | hdc 命令 | 参数 | 说明 |
|--------|---------|------|------|
| `hdc_app_install` | `hdc [-t sn] app install [-r] [-s] <hap>` | `hap_path: str, replace: bool, shared: bool, serial: str?` | 安装 HAP 包到设备 |
| `hdc_app_uninstall` | `hdc [-t sn] app uninstall [-s] <bundlename>` | `bundle_name: str, shared: bool, serial: str?` | 从设备卸载应用 |

### 5.4 Shell 命令（shell.py）— 1 个工具

| 工具名 | hdc 命令 | 参数 | 说明 |
|--------|---------|------|------|
| `hdc_shell` | `hdc [-t sn] shell <cmd>` | `command: str, serial: str?` | ⚠️ 高权限工具：在设备上执行任意 shell 命令，完全透传。MCP description 中需明确警告 AI 在执行破坏性操作前须请求用户确认 |

### 5.5 日志（log.py）— 8 个工具

| 工具名 | hdc 命令 | 参数 | 说明 |
|--------|---------|------|------|
| `hdc_hilog` | `hdc hilog [opts]` | `serial: str?, tag: str?, domain: str?, level: Literal["DEBUG","INFO","WARN","ERROR","FATAL"]?, pid: int?, regex: str?, head: int?, tail: int?, lines: int?, timeout: int?` | 实时抓取日志，支持全量过滤参数。**`lines` 与 `timeout` 至少提供一个**，默认 `lines=200`；输出超过限制时保留最后 N 行 |
| `hdc_hilog_clear` | `hdc hilog -r` | `serial: str?` | 清除设备日志缓冲区 |
| `hdc_hilog_buffer_info` | `hdc hilog -g` | `serial: str?` | 查看日志缓冲区大小信息 |
| `hdc_hilog_write_start` | `hdc hilog -w start` | `serial: str?` | 开启日志落盘写入 |
| `hdc_hilog_write_stop` | `hdc hilog -w stop` | `serial: str?` | 停止日志落盘写入 |
| `hdc_hilog_write_query` | `hdc hilog -w query` | `serial: str?` | 查询日志落盘状态 |
| `hdc_hilog_privacy` | `hdc hilog -p on/off` | `enable: bool, serial: str?` | 开启/关闭隐私日志输出 |
| `hdc_hilog_kernel` | `hdc hilog -k on/off` | `enable: bool, serial: str?` | 开启/关闭内核日志落盘 |

### 5.6 端口转发（forward.py）— 3 个工具

| 工具名 | hdc 命令 | 参数 | 说明 |
|--------|---------|------|------|
| `hdc_fport_add` | `hdc fport tcp:<local> tcp:<remote>` | `local_port: int, remote_port: int, serial: str?` | 添加 TCP 端口转发规则 |
| `hdc_fport_rm` | `hdc fport rm tcp:<local> tcp:<remote>` | `local_port: int, remote_port: int, serial: str?` | 删除端口转发规则 |
| `hdc_fport_list` | `hdc fport ls` | `serial: str?` | 列出所有端口转发规则 |

### 5.7 服务管理（server_tools.py）— 2 个工具

| 工具名 | hdc 命令 | 参数 | 说明 |
|--------|---------|------|------|
| `hdc_start_server` | `hdc start` | 无 | 启动 hdc 服务端 |
| `hdc_kill_server` | `hdc kill` | 无 | 停止 hdc 服务端 |

---

## 6. 数据流

```
AI 助手
  │  调用 MCP 工具（工具名 + 参数）
  ▼
server.py（MCP Server）
  │  路由到对应工具函数
  ▼
tools/*.py（工具层）
  │  参数校验、构建 args 列表
  ▼
executor.py（执行器）
  │  subprocess 调用 hdc 二进制
  ▼
hdc 进程（本机）
  │  通过 USB/TCP 操作设备
  ▼
HarmonyOS 设备
```

---

## 7. 错误处理策略

| 错误类型 | 处理方式 |
|---------|---------|
| hdc 未找到 | 返回明确错误信息，提示配置 `HDC_PATH` 环境变量 |
| 设备未连接 | 透传 hdc 错误输出，AI 可据此提示用户检查连接 |
| 命令执行超时 | 返回超时错误，提示增大 `HDC_TIMEOUT` 配置 |
| 命令执行失败 | 返回 stderr 内容及 returncode，便于 AI 诊断 |
| 参数不合法 | 工具层校验，返回参数错误说明 |

---

## 8. 跨平台处理

- `config.py` 使用 `platform.system()` 检测平台（`Darwin` / `Windows` / `Linux`）
- hdc 路径查找逻辑按平台分支处理，Linux 用户建议通过 `HDC_PATH` 手动指定
- 所有子进程调用统一走 `executor.py`，不使用 `shell=True`
- 文件路径参数由调用方（AI）负责提供正确格式，工具层不做路径转换

---

## 9. 发布配置（pyproject.toml 关键配置）

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
```

用户通过以下方式运行：
```bash
uvx hdc-mcp
```

Claude Desktop 配置示例：
```json
{
  "mcpServers": {
    "hdc": {
      "command": "uvx",
      "args": ["hdc-mcp"],
      "env": {
        "HDC_PATH": "/path/to/hdc"
      }
    }
  }
}
```

---

## 10. 测试策略

- **测试框架：** `pytest` + `pytest-mock`，代码覆盖率目标 80%+
- **单元测试：** mock `executor.py` 的 `run` 方法，测试各工具的参数构建逻辑和边界校验（如 `hdc_hilog` 无 `lines`/`timeout` 时的报错）
- **集成测试：** 连接真实设备或使用 hdc 模拟器验证端到端流程
- **跨平台测试：** 在 macOS 和 Windows 上分别验证路径解析和命令执行
- **CI/CD：** GitHub Actions，在 `push` / `pull_request` 时自动运行单元测试（macOS + Windows 矩阵）
