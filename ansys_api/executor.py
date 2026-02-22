import subprocess
from ansys_api.models import UserTask, CalculationResult


class UserTaskExcutor:
    """
    A class to execute Ansys Fluent with a given configuration file.
    """
    def __init__(self, user_task: UserTask):
        self.user_task = user_task
        self.command = [
            self.user_task.executor.pure_path,
            "-B",
            "-F", user_task.project_path, 
            # "-F", 'C:/Users/Lenar/AnsysProjects/pipe_3.wbpj',
            "-R", user_task.config.path,
        ]

    def __call__(self, *args, **kwds):
        try:
            result = subprocess.run(self.command, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"An error occurred while executing Ansys Fluent: {result.stderr}")
                raise RuntimeError("ANSYS failed")

            else:
                print(f"Ansys Fluent executed successfully: {result.stdout}")
        except Exception as e:
            print(f"Exception occurred while executing Ansys Fluent: {e}")


def execute_user_task(user_task: UserTask):
    """
    A function to execute Ansys Fluent with a given UserTask instance.
    """
    executor = UserTaskExcutor(user_task)
    try:
        print("Start calculation...")
        executor()
        print("Calculation completed.")
        print("Saving result...")
        CalculationResult.objects.create(
            result=user_task.result_path,
            user_task=user_task
        )
        print("Result saved.")
    except Exception as e:
        print(f"Exception occurred while executing user task: {e}")
