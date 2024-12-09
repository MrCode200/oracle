from threading import Thread, Event
from time import sleep
from rich.console import Console
from prompt_toolkit import prompt
from rich.prompt import Confirm

console = Console()
app_thread = None
stop_event = Event()

def init_app():
    console.log("[bold green]App is running...[/bold green]")
    stop_event.wait(10)  # Simulate a long-running process that checks for stop_event
    console.log("[bold yellow]App finished.[/bold yellow]")

def start_app() -> None:
    global app_thread, stop_event
    if app_thread and app_thread.is_alive():
        console.print("[bold red]App is already running![/bold red]")
        return

    stop_event.clear()  # Reset the stop event
    app_thread = Thread(target=init_app, daemon=True)
    app_thread.start()
    console.print("[bold green]App started successfully![/bold green]")

def stop_app() -> None:
    global app_thread, stop_event
    if not app_thread or not app_thread.is_alive():
        console.print("[bold yellow]App is not running.[/bold yellow]")
        return

    if Confirm.ask("Are you sure you want to stop the app?", default=False):
        stop_event.set()  # Signal the thread to stop
        app_thread.join()  # Wait for the thread to finish
        console.print("[bold green]App stopped successfully![/bold green]")
    else:
        console.print("[bold cyan]Operation canceled.[/bold cyan]")
