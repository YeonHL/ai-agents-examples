import click
from server import app


@click.command()
@click.option(
    "--transport",
    default="streamable-http",
    help="Transport protocol",
)
@click.option("--host", default="127.0.0.1", help="Host to listen on for HTTP")
@click.option("--port", default=8000, help="Port to listen on for HTTP")
@click.option(
    "--log-level",
    default="INFO",
    help="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
)
def main(
    transport: str,
    host: str,
    port: int,
    log_level: str,
) -> int:
    path: str = "/mcp"

    app.run(
        transport=transport,
        host=host,
        port=port,
        log_level=log_level.lower(),
        path=path,
    )

    return 0


if __name__ == "__main__":
    main()
