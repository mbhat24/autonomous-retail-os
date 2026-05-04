import typer
import uvicorn
from rich.console import Console

from autonomous_retail_os.database import init_db

app = typer.Typer(help="Autonomous Retail OS command line")
console = Console()


@app.command()
def init() -> None:
    init_db()
    console.print("[green]Database initialized[/green]")


@app.command()
def server(host: str = "127.0.0.1", port: int = 8080, reload: bool = False) -> None:
    console.print(f"[green]Starting Autonomous Retail OS at http://{host}:{port}[/green]")
    uvicorn.run("autonomous_retail_os.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    app()
