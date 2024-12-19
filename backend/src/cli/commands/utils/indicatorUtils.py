from rich.table import Table, box

def create_param_table(class_kwargs: dict[str, any]) -> Table:
    param_table = Table(show_header=True, header_style="bold cyan", box=box.ROUNDED, title="Parameters", style="bold")
    param_table.add_column("Parameter", style="bold green")
    param_table.add_column("Value", style="bold yellow")
    param_table.add_column("Type", style="bold magenta")

    for param_name, param in class_kwargs.items():
        param_table.add_row(param_name, str(param), str(param.__class__.__name__))

    return param_table