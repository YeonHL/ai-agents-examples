import asyncio

from fastmcp import Client
from server import transport

stdio_client = Client(transport)


async def main() -> None:
    async with stdio_client:
        print(f"Client connected: {stdio_client.is_connected()}")
        await stdio_client.ping()

        tools = await stdio_client.list_tools()
        print(f"Available tools: {tools}")
        resources = await stdio_client.list_resources()
        print(f"Available resources: {resources}")

        if any(tool.name == "greet" for tool in tools):
            result = await stdio_client.call_tool("greet", {"name": "World"})
            print(f"Greet result: {result}")

    # 여기서 연결이 자동으로 닫힘
    print(f"Client connected: {stdio_client.is_connected()}")


if __name__ == "__main__":
    asyncio.run(main())
