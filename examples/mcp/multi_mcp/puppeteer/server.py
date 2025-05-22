from fastmcp import FastMCP
from transports import DockerStdioTransport

transport = DockerStdioTransport(
    args=["--init", "-e", "DOCKER_CONTAINER=true", "mcp/puppeteer"]
)
app = FastMCP.as_proxy(transport)


if __name__ == "__main__":
    app.run(transport="stdio")
