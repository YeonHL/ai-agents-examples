import asyncio
import logging
from collections.abc import AsyncGenerator

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from interfaces.schemas import ChatRequest, ChatResponse
from server import container

from src.application.ports.agent_service import AgentService

logger = logging.getLogger("company_researcher")


company_researcher_router = APIRouter(
    prefix="/company-researcher",
    tags=["company-researcher"],
)


@inject
@company_researcher_router.post(path="/chat")
async def chat(
    chat_request: ChatRequest,
    agent_service: AgentService = Depends(Provide[container.agent_service]),
) -> StreamingResponse:
    """
    사용자 메시지를 받아 Agent의 응답을 스트리밍으로 반환합니다.

    **Request Body:**

    - `message` (list[dict]): 사용자와의 대화 기록.
    - `session_id` (str): 대화를 식별하는 세션 ID.

    **Streaming Response:**

    - `media_type`: "text/event-stream" (Server-Sent Events).
    - 각 이벤트의 `data` 필드는 **ChatResponse** 스키마를 따르는 JSON 문자열입니다.
        - `{"content": {"type": "start", "output": "..."}}`
        - `{"content": {"type": "action", "output": "..."}}`
        - `{"content": {"type": "result", "output": "..."}}`
        - `{"content": {"type": "end", "output": "..."}}`
    """

    async def stream_agent_response(chat_request: ChatRequest) -> AsyncGenerator:
        """
        Agent의 응답을 단계별로 생성하고 스트리밍하는 비동기 제너레이터입니다.
        각 단계의 결과는 ChatResponse 스키마에 맞춰 JSON 형태로 반환됩니다.
        """
        start_content = {
            "type": "start",
            "output": "기업 서치 시작",
        }
        start_response = ChatResponse(content=start_content)
        yield f"data: {start_response.model_dump_json()}\n\n"
        await asyncio.sleep(0.5)

        user_message = chat_request.message[-1]["content"]
        action_content = {
            "type": "action",
            "action": "검색",
            "action_desc": "정보 검색",
            "output": f"'{user_message}'에 대한 검색 수행",
        }
        action_response = ChatResponse(content=action_content)
        yield f"data: {action_response.model_dump_json()}\n\n"
        await asyncio.sleep(1)

        result_content = {
            "type": "result",
            "output": "검색 결과: 해당 정보에 대한 리서치 결과를 찾았습니다.",
        }
        result_response = ChatResponse(content=result_content)
        yield f"data: {result_response.model_dump_json()}\n\n"
        await asyncio.sleep(0.5)

        end_content = {"type": "end", "output": "Agent 종료"}
        end_response = ChatResponse(content=end_content)
        yield f"data: {end_response.model_dump_json()}\n\n"

    return StreamingResponse(
        content=stream_agent_response(chat_request),
        media_type="text/event-stream",
    )
