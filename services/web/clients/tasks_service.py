import requests
from django.conf import settings


class TaskServiceError(Exception):
    pass


class TaskServiceUnavailable(TaskServiceError):
    pass

def create_task(user_id: int, payload: dict):
    pass

def get_tasks(user_id: int):
    pass

def get_a_task(user_id: int, task_id: int):
    pass

def edit_a_task(user_id: int, task_id: int):
    pass

def delete_a_task(user_id: int, task_id: int):
    pass