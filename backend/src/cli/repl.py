from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.console import Console
from rich.prompt import Prompt
import time

from src.utils.registry import profile_registry

import logging

logger = logging.getLogger("oracle.app")

from src.app import init_app

def repl():
    console = Console()

    init_app(repl=True)

    from src.cli import app

    while True:
        print("")
        command = Prompt.get_input(console,"[bold ]> ", password=False)
        if command == "exit":
            if Prompt.ask("Are you sure you want to exit?", choices=["y", "n"], default="n"):
                break

        try:
            app(command.split())

        except SystemExit as e:
            if e.code != 0:
                print(f"Command failed with code: {e.code}")

    with Progress(
        SpinnerColumn(finished_text=":white_check_mark: "),
        TextColumn("[progress.description]{task.description} {task.completed}/{task.total}"),
    ) as progress:
        profiles = profile_registry.get().values()

        deactivate_task = progress.add_task(description="[bold yellow]Deactivating all profiles...", total=len(profiles))
        sleep_task = progress.add_task(description="[bold yellow]Closing Oracle...", total=5)

        for profile in profiles:
            progress.update(deactivate_task, advance=1)
            profile.deactivate()

        progress.update(deactivate_task, description="[bold green]All Profiles Deactivated Successfully")

        logger.info("All Profiles Deactivated Successfully. Closing Oracle...")

        for _ in range(5):
            progress.update(sleep_task, advance=1)
            time.sleep(1)

        progress.update(sleep_task, description="[bold green]Closed")