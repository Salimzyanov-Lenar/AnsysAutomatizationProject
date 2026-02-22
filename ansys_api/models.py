import re

from django.db import models
from ansys_api.regex import PATTERN_FOR_RESULT_CSV_FILE, PATTERN_FOR_PARAMS, PATTERN_FOR_VATIABLES, PATTERN_WBPJ


def _find_result_path(config_path: str) -> str:
    """
    Open file and find result csv file from config file, return result csv file path 
    """
    with open(config_path, 'r') as f:
        content = f.read()
        match = PATTERN_FOR_RESULT_CSV_FILE.search(content)
        if match:
            return match.group(1)
    return ""


def _find_parameters(config_path: str) -> dict[str, str]:
    """
    Open file and find parameters and valules from config file, return parameters dict
    """
    parameters = {}
    with open(config_path, 'r') as f:
        content = f.read()
        params_matches = PATTERN_FOR_PARAMS.findall(content)
        variables_matches = PATTERN_FOR_VATIABLES.findall(content)
        for match in params_matches:
            parameters[match[0]] = match[1]
        for match in variables_matches:
            parameters[match[0]] = match[1]
    return parameters


def _find_project_path(config_path: str) -> str:
    """
    Open file and find project .wbpj file path from config file, return project .wbpj file path 
    """
    with open(config_path, 'r') as f:
        content = f.read()
        match = PATTERN_WBPJ.search(content)
        if match:
            return match.group(2)
    return ""


class Executor(models.Model):
    """
    Contains path to executor ansys module
    """
    path = models.FileField(upload_to='user_executors/')
    pure_path = models.TextField(null=True, blank=True, help_text="Leave blank will be filled after save")

    def __str__(self):
        return f"Executor(name={self.path.name})"


class UserTask(models.Model):
    """
    Contains config for ansys executor 
    """
    config = models.FileField(upload_to='user_configs/')
    project = models.FileField(upload_to='user_configs/')
    executor = models.ForeignKey(Executor, on_delete=models.CASCADE, related_name="configs")
    created_at = models.DateTimeField(auto_now_add=True)

    result_path = models.TextField(null=True, blank=True, help_text="Leave blank will be filled after save")
    project_path = models.TextField(null=True, blank=True, help_text="Leave blank will be filled after save")
    parameters = models.JSONField(default=dict, null=True, blank=True, help_text="Leave blank will be filled after save")

    def __str__(self):
        return f"UserTask(config={self.config.name}, executor={self.executor})"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.config:
            self.result_path = _find_result_path(self.config.path)
            self.parameters = _find_parameters(self.config.path)
            self.project_path = _find_project_path(self.config.path)
            super().save(update_fields=['result_path', 'project_path', 'parameters'])


class CalculationResult(models.Model):
    """
    Contains result of ansys executor calculation
    """
    result = models.FileField(upload_to='calculation_results/')
    user_task = models.ForeignKey(UserTask, on_delete=models.CASCADE, related_name="results")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CalculationResult(result={self.result}, user_task={self.user_task})" 
