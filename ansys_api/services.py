import re
import csv
import uuid
import matplotlib.pyplot as plt
from io import BytesIO
from django.core.files.base import ContentFile
from typing import Any
from ansys_api.models import UserTask, CalculationResult, Graph


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


def parse_result_from_calculation_result(calculation_result: CalculationResult) -> dict[str, float]:
    
    parameters: list[str] | None = None
    values: list[float] | None = None

    with open(calculation_result.result.path, newline='', encoding='utf-8-sig') as f:
        reader = csv.reader(f, delimiter='\t')

        for row in reader:
            row_as_string: str = row[0]

            string_parts: list[str] = row_as_string.split(',')
            string_parts: list[str] = [part.strip() for part in string_parts]

            if string_parts[0] == '#' and any('P1 ' in part for part in string_parts):
                parameters = string_parts[1:]
                continue
        
            if 'DP' in string_parts[0]:
                values = [float(part) for part in string_parts[1:]]
                break

    result = {key: value for key, value in zip(parameters, values)} if parameters and values else {}
    return result


def _build_graph_with_experiement_result(graph: Graph) -> None:
    user_task_results = graph.user_task.results.all()

    graph_values = [
        parse_result_from_calculation_result(r)
        for r in user_task_results
    ]

    if not graph_values:
        return

    # ключи
    x_key = list(graph_values[0].keys())[0]
    y_key = list(graph_values[0].keys())[1]

    # сортировка (важно)
    graph_values.sort(key=lambda d: d[x_key])

    x = [d[x_key] for d in graph_values]
    y = [d[y_key] for d in graph_values]

    # строим график
    plt.figure()
    plt.plot(x, y)
    plt.xlabel(x_key)
    plt.ylabel(y_key)
    plt.grid(True)

    # сохраняем в память
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300)
    plt.close()
    buffer.seek(0)

    graph.graph.save(f'graph_{uuid.uuid4().hex}.png', ContentFile(buffer.read()), save=True)