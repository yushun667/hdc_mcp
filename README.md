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
        "HDC_PATH": "/path/to/hdc"
      }
    }
  }
}
```

> `HDC_PATH` 为可选项，macOS/Windows 会自动探测 DevEco Studio 安装的 hdc。

## 前置条件

- 已安装 [DevEco Studio](https://developer.huawei.com/consumer/cn/deveco-studio/)（包含 hdc 工具）
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
