import asyncio
import logging
from collections.abc import AsyncGenerator

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from interfaces.schemas import ChatRequest, ChatResponse

from src.application.ports.agent_service import AgentService
from src.server import container

logger = logging.getLogger("interfaces")


router = APIRouter()


@inject
@router.post(
    path="/responses",
    tags=["agent"],
)
async def responses(
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
        - `{"type": "start", "output": "..."`
        - `{"type": "action", "output": "..."}`
        - `{"type": "result", "output": "..."}`
        - `{"type": "end", "output": "..."}`
    """

    async def stream_agent_response(chat_request: ChatRequest) -> AsyncGenerator:
        """
        Agent의 응답을 단계별로 생성하고 스트리밍하는 비동기 제너레이터입니다.
        각 단계의 결과는 ChatResponse 스키마에 맞춰 JSON 형태로 반환됩니다.
        """
        # 시작 메시지
        start_response = ChatResponse(type="start", output="기업 서치 시작")
        yield f"data: {start_response.model_dump_json(exclude_none=True)}\n\n"
        await asyncio.sleep(0.5)

        # 액션 메시지
        user_message = chat_request.message[-1]["content"]
        action_response = ChatResponse(
            type="action",
            action="검색",
            action_desc="정보 검색",
            output=f"'{user_message}'에 대한 검색 수행",
        )
        yield f"data: {action_response.model_dump_json(exclude_none=True)}\n\n"
        await asyncio.sleep(1)

        # 결과 메시지
        result_response_1 = ChatResponse(
            type="result",
            output="검색 결과: ",
        )
        yield f"data: {result_response_1.model_dump_json(exclude_none=True)}\n\n"
        result_response_2 = ChatResponse(
            type="result",
            output="해당 정보에 대한 ",
        )
        yield f"data: {result_response_2.model_dump_json(exclude_none=True)}\n\n"
        result_response_3 = ChatResponse(
            type="result",
            output="리서치 결과를 찾았습니다.",
        )
        yield f"data: {result_response_3.model_dump_json(exclude_none=True)}\n\n"
        await asyncio.sleep(0.5)

        # 종료 메시지
        end_response = ChatResponse(type="end", output="Agent 종료")
        yield f"data: {end_response.model_dump_json(exclude_none=True)}\n\n"

    return StreamingResponse(
        content=stream_agent_response(chat_request),
        media_type="text/event-stream",
    )
