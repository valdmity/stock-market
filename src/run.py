import click
import uvicorn


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option(
    '--port',
    default=8000,
    help='Server port',
)
def web(port: int) -> None:
    from app import app

    uvicorn.run(
        app,
        host='0.0.0.0',
        port=port,
        access_log=False,
        lifespan='on',
    )


if __name__ == '__main__':
    cli()
