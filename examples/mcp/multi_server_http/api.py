import uvicorn
from fastapi import FastAPI
from server import app

# ASGI 앱 생성
mcp_app = app.http_app(path="/mcp")

# FastAPI 앱을 생성하고 MCP 서버 마운트
app = FastAPI(lifespan=mcp_app.lifespan)
app.mount("", mcp_app)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
