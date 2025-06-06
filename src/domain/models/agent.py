from typing import Union

from pydantic import BaseModel, ConfigDict, Field, SecretStr


class SamplingParameter(BaseModel):
    """LLM 모델의 샘플링 매개변수를 정의하는 클래스.

    이 클래스는 언어 모델의 텍스트 생성을 제어하는 다양한 매개변수들을 포함합니다.
    각 매개변수는 모델의 출력을 미세 조정하는 데 사용됩니다.

    Attributes:
        temperature: 샘플링 온도 값. 높을수록 더 창의적인 출력을 생성.
        max_retries: 생성 시도 최대 횟수.
        presence_penalty: 토큰 중복 출현 패널티.
        frequency_penalty: 토큰 빈도 기반 중복 패널티.
        seed: 생성 결과 재현을 위한 시드값.
        logprobs: 로그 확률 반환 여부.
        top_logprobs: 각 토큰 위치에서 반환할 가장 가능성 높은 토큰 수.
        logit_bias: 특정 토큰의 출현 가능성 수정을 위한 편향값.
        streaming: 결과의 스트리밍 여부.
        n: 각 프롬프트당 생성할 채팅 완성 수.
        top_p: 각 단계에서 고려할 토큰의 총 확률 질량.
        max_tokens: 생성할 최대 토큰 수.
        reasoning_effort: 추론 모델의 추론 노력 제약 수준.
    """

    model_config = ConfigDict(frozen=True)

    temperature: float | None = Field(
        default=None, description="샘플링 온도 값. 높을수록 더 창의적인 출력을 생성."
    )
    max_retries: int | None = Field(
        default=None, description="생성 시도의 최대 재시도 횟수."
    )
    presence_penalty: float | None = Field(
        default=None,
        description="토큰의 중복 출현을 제어하는 패널티 값. 높을수록 중복 출현을 억제.",
    )
    frequency_penalty: float | None = Field(
        default=None,
        description="토큰의 빈도에 기반한 중복 제어 패널티 값. \
                    높을수록 자주 사용된 토큰의 재사용 억제.",
    )
    seed: int | None = Field(
        default=None, description="결과의 일관성을 위한 난수 생성 시드값."
    )
    logprobs: bool | None = Field(
        default=None, description="각 토큰의 로그 확률값 반환 여부."
    )
    top_logprobs: int | None = Field(
        default=None, description="각 위치에서 반환할 가장 가능성 높은 토큰의 개수."
    )
    logit_bias: dict[int, int] | None = Field(
        default=None,
        description="특정 토큰의 출현 가능성을 수정하기 위한 바이어스 값 매핑.",
    )
    streaming: bool | None = Field(
        default=None, description="생성된 텍스트를 스트리밍 방식으로 반환할지 여부."
    )
    n: int | None = Field(
        default=None, description="각 프롬프트에 대해 생성할 응답의 수."
    )
    top_p: float | None = Field(
        default=None,
        description="누적 확률이 이 값을 초과하는 토큰만 샘플링에 포함 (핵 샘플링).",
    )
    max_tokens: int | None = Field(
        default=None, description="응답으로 생성할 최대 토큰 수."
    )
    reasoning_effort: str | None = Field(
        default=None,
        description="추론 모델이 답변 생성에 들일 노력의 수준을 제어하는 설정값.",
    )


class ModelInfo(BaseModel):
    """LLM 모델 정보를 정의하는 클래스.

    모델의 기본 정보와 샘플링 매개변수를 포함합니다.

    Attributes:
        name: 사용할 LLM 모델 이름.
        provider: 모델 제공자.
        api_key: 모델 API 키.
    """

    model_config = ConfigDict(frozen=True)

    name: str = Field(description="사용할 LLM 모델 이름.")
    provider: str = Field(default="", description="모델 제공자.")
    api_key: SecretStr = Field(default=SecretStr(""), description="모델 API 키.")

    @property
    def identifier(self) -> str:
        """모델 식별자

        Returns:
            str: 'provider:name' 형식의 모델 식별자. provider가 없는 경우 name만 반환.
        """
        return f"{self.provider}:{self.name}" if self.provider else self.name


class Agent(BaseModel):
    """
    Attributes:
        sampling_parameters: 모델의 샘플링 매개변수.
    """

    name: str = Field(description="에이전트 이름.")
    model_info: ModelInfo = Field(description="LLM 모델의 정보.")
    sampling_parameters: SamplingParameter = Field(
        default_factory=SamplingParameter, description="모델의 샘플링 매개변수."
    )

    def update_model_info(
        self, name: str, provider: str, api_key: Union["SecretStr", str]
    ) -> None:
        """모델 정보 업데이트

        Args:
            name: 업데이트할 모델 이름.
            provider: 업데이트할 모델 제공자.
            api_key: 업데이트할 모델 API 키.
        """
        self.model_info = ModelInfo(name=name, provider=provider, api_key=api_key)  # type: ignore (자동 변환 수행)

    def update_sampling_parameters(
        self,
        temperature: float | None = None,
        max_retries: int | None = None,
        presence_penalty: float | None = None,
        frequency_penalty: float | None = None,
        seed: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        logit_bias: dict[int, int] | None = None,
        streaming: bool | None = None,
        n: int | None = None,
        top_p: float | None = None,
        max_tokens: int | None = None,
        reasoning_effort: str | None = None,
    ) -> None:
        """샘플링 매개변수 업데이트

        기존 매개변수에서 전달받은 매개변수만 업데이트합니다.
        None으로 전달된 매개변수는 기존 값을 유지합니다.

        Args:
            temperature: 샘플링 온도 값
            max_retries: 생성 시도 최대 횟수
            presence_penalty: 토큰 중복 출현 패널티
            frequency_penalty: 토큰 빈도 기반 중복 패널티
            seed: 생성 결과 재현을 위한 시드값
            logprobs: 로그 확률 반환 여부
            top_logprobs: 각 토큰 위치에서 반환할 가장 가능성 높은 토큰 수
            logit_bias: 특정 토큰의 출현 가능성 수정을 위한 편향값
            streaming: 결과의 스트리밍 여부
            n: 각 프롬프트당 생성할 채팅 완성 수
            top_p: 각 단계에서 고려할 토큰의 총 확률 질량
            max_tokens: 생성할 최대 토큰 수
            reasoning_effort: 추론 모델의 추론 노력 제약 수준
        """
        new_parameters = {
            k: v for k, v in locals().items() if k != "self" and v is not None
        }
        current_parameters = self.sampling_parameters.model_dump(exclude_none=True)
        updated_parameters = {**current_parameters, **new_parameters}
        self.sampling_parameters = SamplingParameter(**updated_parameters)
