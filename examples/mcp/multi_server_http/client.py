import asyncio

from fastmcp import Client

puppeteer_client = Client("http://127.0.0.1:8000/mcp/puppeteer")


async def call_puppeteer() -> None:
    async with puppeteer_client:
        print(f"Client connected: {puppeteer_client.is_connected()}")
        await puppeteer_client.ping()

        tools = await puppeteer_client.list_tools()
        print(f"Available tools: {tools}")
        resources = await puppeteer_client.list_resources()
        print(f"Available resources: {resources}")

        if any(tool.name == "greet" for tool in tools):
            result = await puppeteer_client.call_tool("greet", {"name": "World"})
            print(f"Greet result: {result}")

    # 여기서 연결이 자동으로 닫힘
    print(f"Client connected: {puppeteer_client.is_connected()}")


if __name__ == "__main__":
    asyncio.run(call_puppeteer())
