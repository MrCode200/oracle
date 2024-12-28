from typing import Callable, Optional
from inspect import signature, Parameter

def check_annotations_for_init(cls: type) -> None:
    """
    Check if all parameters have an annotation

    :param cls: The cls to check
    """
    params: dict[str, Parameter] = signature(cls).parameters

    for param_name, param in params.items():
        if param.annotation == Parameter.empty:
            raise Exception(f"Parameter {param_name} has no annotation")