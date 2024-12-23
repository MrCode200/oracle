from rich.table import Table, box
# TODO: change name to create paramm indicator table
def create_param_table(class_kwargs: dict[str, any]) -> Table:
    param_table = Table(header_style="bold cyan", box=box.ROUNDED, style="bold")
    param_table.add_column("", style="dim")
    param_table.add_column("Parameter", style="bold green")
    param_table.add_column("Value", style="bold yellow")
    param_table.add_column("Type", style="bold magenta")

    i: int = 1
    for param_name, param in class_kwargs.items():
        param_table.add_row(str(i), param_name, str(param), str(param.__class__.__name__))
        i += 1

    return param_table


# TODO: add this to the crud indicator Commands
def create_extra_indicator_table():
    ...