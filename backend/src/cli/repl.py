import logging
import time

from prompt_toolkit.styles import Style
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory

from src.utils.registry import profile_registry
from src.cli import command_list

logger = logging.getLogger("oracle.app")

from src.app import init_app

word_completer_style = Style.from_dict({
    "prompt": "bold fg:pink",
    "completion-menu.completion": "fg:gray bg:default",
    "completion-menu.completion.current": "fg:lightgrey bg:darkcyan bold",
    "bottom-toolbar": "bg:darkgray fg:lightgrey italic",
})

history = InMemoryHistory()


def repl():
    init_app(repl=True)

    from src.cli import app

    try:
        while True:
            print("")
            command = prompt("> ",
                             completer=WordCompleter(words=["exit"] + command_list, sentence=True),
                             style=word_completer_style,
                             history=history)

            if command == "exit":
                if Prompt.ask("Are you sure you want to exit?", choices=["y", "n"], default="y") == "y":
                    break

            try:
                command_split = command.split()
                app(command_split)

            except SystemExit as e:
                if e.code != 0:
                    print(f"Command failed with code: {e.code}")

    finally:
        with Progress(
                SpinnerColumn(finished_text=":white_check_mark: "),
                TextColumn("[progress.description]{task.description} {task.completed}/{task.total}"),
        ) as progress:
            profiles = profile_registry.get().values()

            deactivate_task = progress.add_task(description="[bold yellow]Deactivating all profiles...",
                                                total=len(profiles))
            close_db_engine_task = progress.add_task(description="[bold yellow]Closing database engine...",
                                                     total=1)
            sleep_task = progress.add_task(description="[bold yellow]Closing Oracle...", total=5)

            for profile in profiles:
                progress.update(deactivate_task, advance=1)
                profile.deactivate()

            progress.update(deactivate_task, description="[bold green]All Profiles Deactivated Successfully")

            from src.database import engine

            engine.dispose()
            progress.update(close_db_engine_task, advance=1, description="[bold green]Database engine closed")

            logger.info("All Profiles Deactivated Successfully. Closing Oracle...")

            for _ in range(5):
                progress.update(sleep_task, advance=1)
                time.sleep(1)

            progress.update(sleep_task, description="[bold green]Closed")
