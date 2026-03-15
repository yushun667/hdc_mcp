# hdc-mcp 使用说明

本文档详细介绍 hdc-mcp 提供的 24 个 MCP 工具的参数、用法和示例。

---

## 目录

- [设备管理](#设备管理)
- [文件传输](#文件传输)
- [应用管理](#应用管理)
- [Shell 命令](#shell-命令)
- [日志（hilog）](#日志hilog)
- [端口转发](#端口转发)
- [服务管理](#服务管理)
- [常见场景示例](#常见场景示例)
- [错误处理说明](#错误处理说明)

---

## 设备管理

### `hdc_list_targets`

列出所有已连接的 HarmonyOS 设备。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `verbose` | `bool` | `false` | 是否显示详细设备信息 |

**示例：**
```
# 列出所有设备（简洁输出）
hdc_list_targets()

# 列出所有设备（详细信息，包含设备状态）
hdc_list_targets(verbose=true)
```

**输出示例：**
```
SN001   USB
SN002   TCP
```

---

### `hdc_target_connect`

通过 TCP/IP 连接网络设备（设备需已开启网络调试模式）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | `str` | ✅ | 设备地址，格式 `host:port` |

**示例：**
```
hdc_target_connect(address="192.168.1.100:5555")
```

---

### `hdc_target_disconnect`

断开网络设备连接。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `address` | `str \| null` | `null` | 设备地址，不传则断开所有网络设备 |

**示例：**
```
# 断开指定设备
hdc_target_disconnect(address="192.168.1.100:5555")

# 断开所有网络设备
hdc_target_disconnect()
```

---

### `hdc_target_reboot`

重启指定设备。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `serial` | `str` | ✅ | 设备序列号（通过 `hdc_list_targets` 获取） |

**示例：**
```
hdc_target_reboot(serial="SN001")
```

---

### `hdc_target_mode`

切换设备连接模式（USB 或 TCP）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mode` | `"usb" \| "tcp"` | ✅ | 目标连接模式 |

**示例：**
```
# 切换到 TCP 网络调试模式
hdc_target_mode(mode="tcp")

# 切回 USB 模式
hdc_target_mode(mode="usb")
```

> 切换到 TCP 模式后需通过 `hdc_target_connect` 重新连接。

---

### `hdc_smode`

切换 hdc 服务器权限模式。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `reset` | `bool` | `false` | `true` 时重置为默认权限模式 |

**示例：**
```
# 提升服务器权限
hdc_smode()

# 重置为默认权限模式
hdc_smode(reset=true)
```

---

## 文件传输

### `hdc_file_send`

推送本地文件或目录到设备。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `local` | `str` | ✅ | 本地文件或目录的绝对路径 |
| `remote` | `str` | ✅ | 设备上的目标路径 |
| `serial` | `str \| null` | — | 设备序列号，连接多台设备时必须指定 |

**示例：**
```
# 推送 HAP 包到设备
hdc_file_send(local="/Users/dev/app.hap", remote="/data/local/tmp/app.hap")

# 多设备时指定序列号
hdc_file_send(local="/tmp/config.json", remote="/data/local/tmp/config.json", serial="SN001")
```

---

### `hdc_file_recv`

从设备拉取文件或目录到本地。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `remote` | `str` | ✅ | 设备上的源文件或目录路径 |
| `local` | `str` | ✅ | 本地目标路径 |
| `serial` | `str \| null` | — | 设备序列号，连接多台设备时必须指定 |

**示例：**
```
# 拉取设备上的日志文件
hdc_file_recv(remote="/data/log/app.log", local="/tmp/app.log")

# 拉取整个目录
hdc_file_recv(remote="/data/local/tmp/crash/", local="/tmp/crash_logs/")
```

---

## 应用管理

### `hdc_app_install`

安装 HAP 包到设备。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `hap_path` | `str` | ✅ 必填 | 本地 HAP 文件路径 |
| `replace` | `bool` | `false` | 替换安装（覆盖已安装的同名应用） |
| `shared` | `bool` | `false` | 安装为共享包（HSP） |
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
# 首次安装
hdc_app_install(hap_path="/tmp/MyApp.hap")

# 覆盖更新（保留用户数据）
hdc_app_install(hap_path="/tmp/MyApp.hap", replace=true)

# 安装共享包（HSP）
hdc_app_install(hap_path="/tmp/MyLib.hsp", shared=true)
```

---

### `hdc_app_uninstall`

从设备卸载应用。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `bundle_name` | `str` | ✅ 必填 | 应用包名，如 `com.example.myapp` |
| `shared` | `bool` | `false` | 卸载共享包（HSP） |
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
# 卸载应用
hdc_app_uninstall(bundle_name="com.example.myapp")

# 卸载共享包
hdc_app_uninstall(bundle_name="com.example.mylib", shared=true)
```

---

## Shell 命令

### `hdc_shell`

> ⚠️ **高权限工具**：此工具将命令完全透传到设备 shell，可执行任意操作（包括删除系统文件等不可逆操作）。执行危险命令前，务必向用户确认。

在 HarmonyOS 设备上执行 shell 命令。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | `str` | ✅ | 要在设备上执行的 shell 命令 |
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
# 查看设备文件
hdc_shell(command="ls /data/local/tmp")

# 查看进程列表
hdc_shell(command="ps -ef | grep myapp")

# 查看设备存储空间
hdc_shell(command="df -h")

# 指定设备执行命令
hdc_shell(command="getprop ro.product.model", serial="SN001")
```

---

## 日志（hilog）

### `hdc_hilog`

抓取设备 hilog 日志，支持丰富的过滤参数。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `serial` | `str \| null` | — | 设备序列号 |
| `tag` | `str \| null` | — | 按日志 tag 过滤（`-t`） |
| `domain` | `str \| null` | — | 按 domain 过滤（`-D`） |
| `level` | `str \| null` | — | 日志级别：`DEBUG` / `INFO` / `WARN` / `ERROR` / `FATAL`（`-l`） |
| `pid` | `int \| null` | — | 按进程 ID 过滤（`-P`） |
| `regex` | `str \| null` | — | 正则表达式过滤（`-e`） |
| `head` | `int \| null` | — | 只取前 N 条日志（`--head`） |
| `tail` | `int \| null` | — | 只取后 N 条日志（`--tail`） |
| `lines` | `int \| null` | `200` | 最大输出行数（`-n`），默认 200 行 |
| `timeout` | `int \| null` | — | 抓取超时秒数（超时后停止） |

> **注意**：`lines` 和 `timeout` 均不传时，默认使用 `lines=200` 防止日志无限输出。

**示例：**
```
# 抓取最新 200 行日志（默认）
hdc_hilog()

# 只抓取 ERROR 级别日志，最多 50 行
hdc_hilog(level="ERROR", lines=50)

# 按 tag 过滤（适合调试特定模块）
hdc_hilog(tag="MyApp", lines=100)

# 按进程 ID 过滤
hdc_hilog(pid=12345, lines=200)

# 正则过滤（查找包含 "crash" 的日志）
hdc_hilog(regex="crash|exception", lines=100)

# 多条件组合过滤
hdc_hilog(tag="NetworkService", level="WARN", lines=50)

# 持续抓取 10 秒（不限行数）
hdc_hilog(timeout=10)

# 只看最后 20 条
hdc_hilog(tail=20)
```

---

### `hdc_hilog_clear`

清除设备日志缓冲区。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
# 清空日志，便于重现问题时获取干净的日志
hdc_hilog_clear()
```

---

### `hdc_hilog_buffer_info`

查看设备日志缓冲区大小信息。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
hdc_hilog_buffer_info()
```

---

### `hdc_hilog_write_start`

开启日志落盘写入，将日志持久化到设备文件系统（便于离线分析）。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
hdc_hilog_write_start()
```

---

### `hdc_hilog_write_stop`

停止日志落盘写入。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
hdc_hilog_write_stop()
```

---

### `hdc_hilog_write_query`

查询日志落盘状态。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
hdc_hilog_write_query()
```

---

### `hdc_hilog_privacy`

开启或关闭隐私日志输出（调试时可开启，发布前建议关闭）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `enable` | `bool` | ✅ | `true` 开启，`false` 关闭 |
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
# 开启隐私日志（调试时可见脱敏前的原始数据）
hdc_hilog_privacy(enable=true)

# 关闭隐私日志
hdc_hilog_privacy(enable=false)
```

---

### `hdc_hilog_kernel`

开启或关闭内核日志落盘。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `enable` | `bool` | ✅ | `true` 开启，`false` 关闭 |
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
hdc_hilog_kernel(enable=true)
```

---

## 端口转发

### `hdc_fport_add`

添加 TCP 端口转发规则，将本地端口映射到设备端口。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `local_port` | `int` | ✅ | 本地监听端口号 |
| `remote_port` | `int` | ✅ | 设备上的目标端口号 |
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
# 将本地 8080 端口转发到设备 8080 端口
hdc_fport_add(local_port=8080, remote_port=8080)

# 端口号不同的映射
hdc_fport_add(local_port=9090, remote_port=8888, serial="SN001")
```

---

### `hdc_fport_rm`

删除端口转发规则。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `local_port` | `int` | ✅ | 本地端口号 |
| `remote_port` | `int` | ✅ | 设备端口号 |
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
hdc_fport_rm(local_port=8080, remote_port=8080)
```

---

### `hdc_fport_list`

列出所有当前端口转发规则。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `serial` | `str \| null` | — | 设备序列号 |

**示例：**
```
hdc_fport_list()
```

---

## 服务管理

### `hdc_start_server`

启动 hdc 服务端守护进程。通常不需要手动调用，hdc 命令会自动启动。

**示例：**
```
hdc_start_server()
```

---

### `hdc_kill_server`

停止 hdc 服务端守护进程。遇到 hdc 连接异常时可尝试重启服务。

**示例：**
```
# 重启 hdc 服务（解决连接异常）
hdc_kill_server()
hdc_start_server()
```

---

## 常见场景示例

### 场景 1：首次连接设备并安装应用

```
# 1. 查看已连接设备
hdc_list_targets()

# 2. 安装 HAP 包
hdc_app_install(hap_path="/Users/dev/build/MyApp.hap")

# 3. 确认安装成功
hdc_shell(command="bm dump -n com.example.myapp")
```

### 场景 2：通过网络连接调试设备

```
# 1. 切换设备到 TCP 模式（需先 USB 连接）
hdc_target_mode(mode="tcp")

# 2. 通过网络连接设备
hdc_target_connect(address="192.168.1.100:5555")

# 3. 确认连接成功
hdc_list_targets()
```

### 场景 3：抓取应用崩溃日志

```
# 1. 先清空历史日志
hdc_hilog_clear()

# 2. 复现崩溃问题后抓取 ERROR 日志
hdc_hilog(level="ERROR", tag="MyApp", lines=500)
```

### 场景 4：多设备并行调试

```
# 查看所有设备
hdc_list_targets(verbose=true)

# 在不同设备上分别安装
hdc_app_install(hap_path="/tmp/app.hap", serial="SN001")
hdc_app_install(hap_path="/tmp/app.hap", serial="SN002")

# 分别抓取日志
hdc_hilog(serial="SN001", level="ERROR", lines=100)
hdc_hilog(serial="SN002", level="ERROR", lines=100)
```

### 场景 5：端口转发调试 HTTP 服务

```
# 将设备上运行的 HTTP 服务转发到本地
hdc_fport_add(local_port=8080, remote_port=8080)

# 调试完成后移除规则
hdc_fport_rm(local_port=8080, remote_port=8080)
```

---

## 错误处理说明

所有工具的返回值均为字符串，错误情况下会包含以下前缀：

| 前缀 | 含义 | 常见原因 |
|------|------|---------|
| `[错误 N]` | hdc 命令返回非零退出码 | 设备未连接、命令参数错误 |
| `[超时]` | 命令执行超时 | 大文件传输、设备响应慢 |
| `[错误]` | 参数校验失败 | 传入了无效的参数值 |

**hdc 未找到时的错误：**
```
找不到 hdc 可执行文件。请通过以下方式之一解决：
1. 安装 DevEco Studio（自动包含 hdc）
2. 设置环境变量 HDC_PATH 指向 hdc 可执行文件的绝对路径
```

**调整超时：** 通过环境变量 `HDC_TIMEOUT` 设置全局超时（默认 30 秒）：
```json
{
  "env": {
    "HDC_TIMEOUT": "120"
  }
}
```
