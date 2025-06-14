from abc import abstractmethod
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

from langchain.chat_models import init_chat_model
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph_supervisor import create_supervisor

from src.application.ports import AgentService

if TYPE_CHECKING:
    from langchain_core.messages import AnyMessage
    from langgraph.prebuilt.chat_agent_executor import (
        StateSchemaType,
        StructuredResponseSchema,
    )
    from langgraph.types import Checkpointer
    from langgraph.utils.runnable import RunnableLike
    from pydantic import SecretStr


class LangGraphAgent(AgentService):
    """LangGraph 기반의 에이전트 구현체입니다.

    이 클래스는 LangGraph를 사용하여 ReAct 패턴을 구현한 에이전트를 제공합니다.
    LLM을 사용하여 추론하고 도구를 활용하여 작업을 수행할 수 있습니다.
    """

    def __init__(
        self,
        name: str,
        model_name: str,
        model_provider: str = "",
        api_key: Union["SecretStr", str] = "",
        sampling_parameters: dict | None = None,
        stream_mode: list[str] | str = "messages",
        response_format: Optional["StructuredResponseSchema"] = None,
        pre_model_hook: Optional["RunnableLike"] = None,
        state_schema: "StateSchemaType" = AgentState,
        checkpointer: Optional["Checkpointer"] = None,
    ) -> None:
        """LangGraphAgent 초기화

        Args:
            name: 에이전트 이름
            model_name: 사용할 LLM 모델 이름
            model_provider: 모델 제공자. 입력할 경우 name과 조합하여 사용. Defaults to "".
            api_key: 모델 API 키. 미입력 시 환경 변수 참조. Defaults to "".
            sampling_parameters: 모델 샘플링 매개변수. Defaults to None.
            stream_mode: 스트리밍 응답 모드. Defaults to "messages".
            response_format: 응답 형식. Defaults to None.
            pre_model_hook: 모델 실행 전 전처리 훅. Defaults to None.
            state_schema: 상태 스키마. Defaults to AgentState.
            checkpointer: 체크포인팅 설정. bool은 하단 참고. Defaults to None.
                - True: 이 서브그래프에 대해 지속성 체크포인팅 활성화
                - False: 부모 그래프에 체크포인터가 있어도 체크포인팅 비활성화
                - None: 부모 그래프로부터 체크포인터 상속
        """
        super().__init__(
            name=name,
            model_name=model_name,
            model_provider=model_provider,
            api_key=api_key,
            sampling_parameters=sampling_parameters,
        )

        _sampling_parameters: dict = self.metadata.sampling_parameters.model_dump(
            exclude_none=True
        )

        self._llm = init_chat_model(
            model=self.metadata.model_info.identifier,
            api_key=self.metadata.model_info.api_key,
            **_sampling_parameters,
        )
        self._stream_mode = stream_mode
        self._tools: list = self._initialize_tools()
        self._response_format = response_format
        self._pre_model_hook = pre_model_hook
        self._state_schema = state_schema
        self._checkpointer = checkpointer
        self._update_graph()

    def _update_graph(self) -> None:
        """에이전트 그래프를 업데이트합니다."""
        self._graph = create_react_agent(
            model=self._llm,
            tools=self._tools,
            prompt=self._prompt,
            response_format=self._response_format,
            pre_model_hook=self._pre_model_hook,
            state_schema=self._state_schema,
            checkpointer=self._checkpointer,
            name=self.metadata.name,
        )
        self._graph_builder = self._graph.builder

    @abstractmethod
    def _prompt(self, state: "AgentState") -> list["AnyMessage"]:
        """프롬프트를 생성하는 메서드입니다.

        Args:
            state: 에이전트 상태

        Returns:
            생성된 메시지 리스트
        """

    @abstractmethod
    def _initialize_tools(self) -> list:
        """에이전트가 사용할 도구 목록을 초기화합니다.
        에이전트가 작업을 수행하는 데 필요한 기본 도구들을 초기화하고 반환합니다.

        Returns:
            list: 초기화된 도구 목록
        """

    async def chat(self, message: list[dict[str, str]], thread_id: str) -> dict:
        config = RunnableConfig(configurable={"thread_id": thread_id})
        return await self._graph.ainvoke({"messages": message}, config=config)

    async def chat_stream(self, message: list, thread_id: str) -> AsyncGenerator:
        config = RunnableConfig(configurable={"thread_id": thread_id})
        async for chunk in self._graph.astream(
            message,
            config=config,  # type: ignore (자동 변환)
            stream_mode=self._stream_mode,  # type: ignore (자동 변환)
        ):
            yield chunk

    def save_graph_png(self, path: str) -> None:
        """그래프를 PNG 이미지로 저장합니다.

        Args:
            path: 저장할 파일 경로
        """
        graph_png = self._graph.get_graph().draw_mermaid_png()
        image_path = Path(path)
        with image_path.open("wb") as f:
            f.write(graph_png)

    def add_tools(self, tools: list) -> None:
        """에이전트에 도구를 추가합니다.

        Args:
            tools: 추가할 도구 목록
        """
        self._tools.extend(tools)
        self._update_graph()

    def update_tools(self, tools: list) -> None:
        """에이전트의 도구를 업데이트합니다.

        Args:
            tools: 적용할 도구 목록
        """
        self._tools = tools
        self._update_graph()

    def reset_tools(self) -> None:
        """에이전트의 도구 목록을 초기화합니다."""
        self.update_tools(self._initialize_tools())

    async def load_mcp_tools(self, tools_transport: dict) -> None:
        """MCP 도구를 로드하고 에이전트에 추가합니다.

        Args:
            tools_transport: MCP 도구 전송 설정
        """
        mcp_client = MultiServerMCPClient(tools_transport)
        mcp_tools = await mcp_client.get_tools()
        self.add_tools(mcp_tools)


class LangGraphSupervisor(LangGraphAgent):
    """LangGraph 기반의 Supervisor 에이전트 구현체입니다.

    이 클래스는 LangGraph를 사용하여 ReAct 패턴을 구현한 Supervisor 에이전트를 제공합니다.
    LLM을 사용하여 추론하고 도구를 활용하여 작업을 수행할 수 있습니다.
    """

    def __init__(
        self,
        name: str,
        agents: list[LangGraphAgent],
        model_name: str,
        model_provider: str = "",
        api_key: Union["SecretStr", str] = "",
        sampling_parameters: dict | None = None,
        stream_mode: list[str] | str = "messages",
        tools: list | None = None,
        response_format: Optional["StructuredResponseSchema"] = None,
        pre_model_hook: Optional["RunnableLike"] = None,
        state_schema: "StateSchemaType" = AgentState,
        checkpointer: Optional["Checkpointer"] = None,
    ) -> None:
        """LangGraphSupervisor 초기화

        Args:
            name: Supervisor 이름
            agents: 관리할 에이전트 목록
            model_name: 사용할 LLM 모델 이름
            model_provider: 모델 제공자. Defaults to "".
            api_key: 모델 API 키. Defaults to "".
            sampling_parameters: 모델 샘플링 매개변수. Defaults to None.
            stream_mode: 스트리밍 응답 모드. Defaults to "messages".
            tools: Supervisor가 사용할 도구 목록. Defaults to None.
            response_format: 응답 형식. Defaults to None.
            pre_model_hook: 모델 실행 전 전처리 훅. Defaults to None.
            state_schema: 상태 스키마. Defaults to AgentState.
            checkpointer: 체크포인팅 설정. Defaults to None.
        """
        self._agents = agents
        super().__init__(
            name=name,
            model_name=model_name,
            model_provider=model_provider,
            api_key=api_key,
            sampling_parameters=sampling_parameters,
            stream_mode=stream_mode,
            tools=tools,
            response_format=response_format,
            pre_model_hook=pre_model_hook,
            state_schema=state_schema,
            checkpointer=checkpointer,
        )
        self._graph_builder = self._graph.builder

    def _update_graph(self) -> None:
        _agents: list = [agent._graph for agent in self._agents]  # noqa: SLF001 (실제로는 내부에서 접근)
        self._graph_builder = create_supervisor(
            agents=_agents,
            model=self._llm,
            tools=self._tools,
            prompt=self._prompt,
            response_format=self._response_format,
            state_schema=self._state_schema,
            supervisor_name=self.metadata.name,
        )
        self._graph = self._graph_builder.compile(
            checkpointer=self._checkpointer, name=self.metadata.name
        )
