from fastmcp.client.transports import StdioTransport


class DockerStdioTransport(StdioTransport):
    """Docker 컨테이너와의 표준 입출력 통신을 위한 전송 클래스.

    Docker 컨테이너를 실행하고 표준 입출력을 통해 통신하는 기능을 제공합니다.

    Attributes:
        command (str): Docker 명령어
        args (list[str]): Docker 실행 인자
        env (dict[str, str]): 환경 변수
        cwd (str): 작업 디렉토리
    """

    def __init__(
        self,
        args: list[str],
        env: dict[str, str] | None = None,
        cwd: str | None = None,
    ) -> None:
        """DockerStdioTransport 초기화.

        기본 명령어로 "docker run -i --rm"을 사용합니다.
        추가 인자와 이미지명은 입력해야 합니다.

        Args:
            args (list[str]): Docker 컨테이너 실행 시 추가할 인자.
            env (dict[str, str] | None, optional): 환경 변수 딕셔너리. Defaults to None.
            cwd (str | None, optional): 작업 디렉토리 경로. Defaults to None.
        """
        command: str = "docker"
        docker_args: list[str] = ["run", "-i", "--rm"]
        docker_args += args
        super().__init__(command=command, args=docker_args, env=env, cwd=cwd)
