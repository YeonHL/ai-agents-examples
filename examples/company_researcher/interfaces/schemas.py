from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """사용자의 채팅 요청을 나타내는 모델"""

    message: list[dict[str, str]] = Field(
        description="사용자와 어시스턴트 간의 대화 기록 리스트. 각 요소는 'role'과 'content'를 키로 가집니다.",
        examples=[[{"role": "user", "content": "오늘 서울 날씨 알려줘"}]],
    )
    session_id: str = Field(
        description="대화의 연속성을 유지하기 위한 세션 식별자",
        examples=["a1b2c3d4-e5f6-7890-1234-567890abcdef"],
    )


class ChatResponse(BaseModel):
    """Agent 서버의 응답을 나타내는 모델"""

    content: dict[str, str] = Field(
        description="Agent의 단계별 응답 내용.",
        examples=[
            {"type": "start", "output": "Agent 시작"},
            {
                "type": "action",
                "action": "검색",
                "action_desc": "검색을 수행하는 기능",
                "output": "오늘 서울 날씨 검색",
            },
            {
                "type": "result",
                "output": "검색 결과: 오늘 서울은 맑고 최고 기온은 25도입니다.",
            },
            {"type": "end", "output": "Agent 종료"},
        ],
    )
