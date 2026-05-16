import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client   # 关键：导入 stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",          # 或 "python3"
        args=["mcp-server-test.py"]
    )

    # stdio_client 返回 (read_stream, write_stream)
    async with stdio_client(server_params) as (read_stream, write_stream):
        # 用这两个流初始化 ClientSession
        async with ClientSession(read_stream, write_stream) as session:
            # 1. 初始化握手
            await session.initialize()

            # 2. 列出工具（可选）
            tools = await session.list_tools()
            print("可用工具:", [tool.name for tool in tools.tools])


            # 3. 调用工具
            result = await session.call_tool(
                "get_top_memory_processes",
                arguments={"limit": 5}
            )
            print("调用结果:", result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
