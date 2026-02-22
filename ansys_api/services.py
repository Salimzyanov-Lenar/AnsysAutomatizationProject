import re
from typing import Any
from ansys_api.models import UserTask


def _replace_parameters(match, new_params):
    param_name = match.group(1)
    old_value = match.group(2)

    if param_name in new_params:
        new_value = new_params.get(param_name, old_value)
        return f'Parameter={param_name}, Expression="{new_value}"'

    return match.group(0)


def _replace_variables(match, new_params):
    var_name = match.group(1)
    old_value = match.group(2)

    if var_name in new_params:
        new_value = new_params.get(var_name, old_value)
        return f'Variables=["{var_name}"], Values=[["{new_value}"]]'
    
    return match.group(0)


def update_config_with_new_params(user_task: UserTask, new_params: dict[str, Any]) -> None:
    """
    Update config file with new parameters and save it to the same path.
    """
    with open(user_task.config.path, 'r') as f:
        content = f.read()

    content = re.sub(
        r'Parameter=(\w+),\s*Expression="([^"]+)"',
        lambda match: _replace_parameters(match, new_params),
        content
    )

    content = re.sub(
        r'Variables=\[(".*?")\],\s*Values=\[\[(".*?")\]\]',
        lambda match: _replace_variables(match, new_params),
        content
    )

    with open(user_task.config.path, 'w') as f:
        f.write(content)
