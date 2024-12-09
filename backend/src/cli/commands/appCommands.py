from src.app import init_app
from threading import Thread
from time import sleep
from typing import Optional
from rich.console import Console
from rich.prompt import Confirm

console = Console()
app_thread: Optional[Thread] = None

"""def init_app():
    console.log("[bold green]App is running...[/bold green]")
    num = 1
    for i in range (100):
        num += 1
        sleep(0.1)
    console.log("[bold yellow]App finished.[/bold yellow]")"""

def start_app() -> None:
    """Starts the application in a background thread."""
    global app_thread
    if app_thread and app_thread.is_alive():
        console.print("[bold red]App is already running![/bold red]")
        return

    app_thread = Thread(target=init_app, daemon=True)
    app_thread.start()
    console.print("[bold green]App started successfully![/bold green]")

def stop_app() -> None:
    """Stops the background application."""
    global app_thread
    if not app_thread or not app_thread.is_alive():
        console.print("[bold yellow]App is not running.[/bold yellow]")
        return

    if Confirm.ask("Are you sure you want to stop the app?", default=False):
        app_thread.join()  # Wait for the thread to finish
        console.print("[bold green]App stopped successfully![/bold green]")
    else:
        console.print("[bold cyan]Operation canceled.[/bold cyan]")