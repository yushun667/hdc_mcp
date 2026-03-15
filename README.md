# hdc-mcp

HarmonyOS hdc 工具的 MCP 服务，让 AI 助手直接操控鸿蒙设备。

## 快速开始

在 Claude Desktop / Cursor 等 MCP 客户端配置文件中添加：

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
