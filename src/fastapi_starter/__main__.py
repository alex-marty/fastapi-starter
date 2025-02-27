import typer
from rich import print as rprint


app = typer.Typer(no_args_is_help=True)


@app.command()
def serve(host: str = "127.0.0.1", port: int = 8000, *, reload: bool = False):
    """Serve the API."""
    import uvicorn

    uvicorn.run("fastapi_starter.api.app:app", host=host, port=port, reload=reload)


# Configuration management
####

config = typer.Typer(name="config", help="Manage configuration.", no_args_is_help=True)
app.add_typer(config)


@config.command("show")
def show_config():
    """Show the current configuration."""
    from fastapi_starter.config import get_config

    config = get_config()
    rprint(config)


if __name__ == "__main__":
    app()
