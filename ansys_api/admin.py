from django.contrib import admin

from ansys_api.models import Executor, UserTask, CalculationResult
from ansys_api.executor import execute_user_task
from ansys_api.services import update_config_with_new_params


@admin.register(Executor)
class ExecutorAdmin(admin.ModelAdmin):
    list_display = ('id', 'path')


@admin.register(UserTask)
class UserTaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'config', 'project', 'executor', 'created_at')

    def save_model(self, request, user_task, form, change):
        super().save_model(request, user_task, form, change)
        update_config_with_new_params(user_task=user_task, new_params=form.cleaned_data["parameters"])
        execute_user_task(user_task)


@admin.register(CalculationResult)
class CalculationResultAdmin(admin.ModelAdmin):
    list_display = ('id', 'result', 'user_task', 'created_at')
