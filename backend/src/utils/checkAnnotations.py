from typing import Callable, Optional
from inspect import signature, Parameter

def check_annotation(func: Callable, ignore: Optional[list[str]]=None) -> None:
    """
    Check if all parameters have an annotation

    :param func: The function to check
    :param ignore: A list of parameters names to ignore when checking
    """
    if ignore is None:
        ignore = []

    params: dict[str, Parameter] = signature(func).parameters

    for param_name, param in params.items():
        if param_name in ignore:
            continue
        if param.annotation == Parameter.empty:
            raise Exception(f"Parameter {param_name} has no annotation")