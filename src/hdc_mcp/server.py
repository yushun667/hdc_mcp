# src/hdc_mcp/server.py
"""
MCP 服务入口模块。
负责创建 FastMCP 实例，从各 tools 模块导入并注册所有工具，启动服务。
"""
from mcp.server.fastmcp import FastMCP

# 创建全局 MCP 服务实例
mcp = FastMCP("hdc-mcp")


def main() -> None:
    """
    MCP 服务主入口，供 uvx/命令行调用。
    通过 mcp.run() 以标准 stdio 模式启动服务。
    """
    mcp.run()


if __name__ == "__main__":
    main()
