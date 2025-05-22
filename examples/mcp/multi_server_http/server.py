from fastmcp import FastMCP
from puppeteer.server import app as puppeteer_app

app = FastMCP(name="MCPServer", instructions="This server provides mcp servers")
app.mount(prefix="puppeteer", server=puppeteer_app)

if __name__ == "__main__":
    app.run(transport="streamable-http", host="127.0.0.1", port=8000, path="/mcp")
