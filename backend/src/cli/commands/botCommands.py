import os
import subprocess
import sys
import tempfile
from typing import Annotated

import psutil
import typer
from rich.console import Console
from rich.progress import Progress
from rich.prompt import Prompt
from rich.text import Text
from src.app import init_app

console = Console()

# Define PID file location
PID_FILE = os.path.join(tempfile.gettempdir(), "monsieur_oracle.pid")

def command_start_app(
        no_process: Annotated[bool, typer.Option(
            "--no-process", "-np",
            help="Runs the app in the current process instead of a separate one."
        )] = False,
        ignore_process_exists: Annotated[bool, typer.Option(
            "--ignore-process-exists", "-ipe",
            help="Starts the app even if it's already. [bold red][underline]Warning:[/underline] This will overwrite the PID file with the current process ID forgetting the current running process.[/bold red]."
        )] = False
) -> None:
    """Start the application."""
    if not ignore_process_exists and os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = int(f.read())

        if psutil.pid_exists(pid):
            console.print(f"[bold yellow]The application is already running with PID {pid}.[/bold yellow]")
            return

    if not no_process:
        console.print("[bold cyan]Creating a new process...[/bold cyan]")

        # Get the virtual environment's Python executable
        venv_python = os.path.join(os.environ["VIRTUAL_ENV"], "Scripts", "python.exe")

        pid = subprocess.Popen(
            [sys.executable, '-m', 'src.app'],
            env={**os.environ, "PYTHONPATH": os.getcwd()},
            stdout=sys.stdout,
            stderr=sys.stderr
        ).pid

        console.print("[bold cyan]Saving process PID...[/bold cyan]")

        # Write the process PID to a file
        with open(PID_FILE, "w") as f:
            f.write(str(pid))

        console.print(f"[bold green]App started in a separate process with PID {pid}.[/bold green]")

    else:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))

        console.print(f"[bold green]Starting app in the current process with PID {os.getpid()}.[/bold green]")
        init_app()


def command_stop_app() -> None:
    """Stop the running application."""
    if not os.path.exists(PID_FILE):
        console.print("[bold red]No PID file found.[/bold red]")

    with open(PID_FILE, "r") as f:
        pid = int(f.read())

    try:
        process = psutil.Process(pid)

        if not process.is_running():
            console.print(
                f"[bold yellow]No running process found with PID {pid}. The application may already be stopped.[/bold yellow]")
            typer.Abort()

        confirm = Prompt.ask(
            Text("[bold yellow]Are you sure you want to stop the application?", style="bold yellow"),
            choices=["y", "n"],
            default="n"
        )

        if confirm == "n":
            typer.Abort()

        console.print(f"[bold cyan]Attempting to terminate process with PID {pid}...[/bold cyan]")

        with Progress() as progress:
            task = progress.add_task("[yellow]Terminating process...", total=100)
            progress.update(task, description="[yellow]Terminating process...", completed=0)
            process.terminate()
            progress.update(task, description="[yellow]Waiting for process to terminate...", completed=50)
            process.wait()
            progress.update(task, description="[green]Process Finished...", completed=100)

        console.print(f"[bold green]Successfully terminated process with PID {pid}.[/bold green]")

    except psutil.NoSuchProcess:
        console.print(
            f"[bold red]No such process found with PID {pid}. The application may not be running.[/bold red]")
    except psutil.AccessDenied:
        console.print(
            f"[bold red]Permission denied while trying to terminate the process with PID {pid}.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred while terminating process: {str(e)}[/bold red]")

def command_status_app() -> None:
    """Check the status of the application."""
    if not os.path.exists(PID_FILE):
        console.print("[bold red]No PID file found.[/bold red]")
        typer.Abort()
        return

    with open(PID_FILE, "r") as f:
        pid = int(f.read())

    try:
        process = psutil.Process(pid)

        console.print(f"[bold]Application Status for process with ID {pid} is: [cyan underline]{process.status()}[/cyan underline].[/bold]")

    except psutil.NoSuchProcess:
        console.print(
            f"[bold yellow]No process found with PID {pid}. The application is not running.[/bold yellow]")
    except psutil.AccessDenied:
        console.print(
            f"[bold red]Permission denied while checking the status of process with PID {pid}.[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred while checking status: {str(e)}[/bold red]")
