from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING, Union

from src.domain.models import Agent

if TYPE_CHECKING:
    from pydantic import SecretStr


class AgentService(ABC):
    """에이전트 서비스 인터페이스

    이 인터페이스는 에이전트 관련 작업을 정의합니다.
    """

    def __init__(
        self,
        name: str,
        model_name: str,
        model_provider: str = "",
        api_key: Union["SecretStr", str] = "",
        sampling_parameters: dict | None = None,
    ) -> None:
        """

        Args:
            model_name: 사용할 LLM 모델 이름
            model_provider (Optional): 모델 제공자, 입력할 경우 name과 조합하여 사용
            api_key (Optional): 모델 API 키, 미입력 시 환경 변수 참조
            sampling_parameters: 모델 샘플링 매개변수 (기본값: None)
        """
        if not sampling_parameters:
            sampling_parameters = {}

        self.metadata = Agent(
            model_info={
                "name": model_name,
                "provider": model_provider,
                "api_key": api_key,
            },  # type: ignore (자동 변환)
            sampling_parameters=sampling_parameters,  # type: ignore (자동 변환)
            name=name,
        )

    @abstractmethod
    async def chat(self, message: list[dict[str, str]], thread_id: str) -> dict:
        """에이전트를 호출하여 메시지를 처리합니다.

        Args:
            message: 사용자 메시지 리스트
            thread_id: 대화 스레드 ID

        Returns:
            dict: 에이전트의 응답
        """

    @abstractmethod
    async def chat_stream(self, message: list, thread_id: str) -> AsyncGenerator:
        """에이전트의 응답을 스트리밍합니다.

        Args:
            message: 사용자 메시지 리스트
            thread_id: 대화 스레드 ID

        Yields:
            dict: 에이전트의 응답 조각
        """
