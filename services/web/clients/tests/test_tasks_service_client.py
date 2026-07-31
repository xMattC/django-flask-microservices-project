import json

import requests
import responses
from django.test import SimpleTestCase, override_settings

from clients.tasks_service import (
    create_task,
    get_a_task,
    get_tasks,
    edit_a_task,
    delete_a_task
)


class TasksClientTests(SimpleTestCase):
    """Test Tasks service client.

    Service Client Test Coverage Checklist:
    - Happy path returns expected data
    - Required headers are sent (e.g. auth / X-User-ID)
    - Network failures raise ServiceUnavailable
    - Upstream 4xx/5xx responses raise ServiceError
    - Invalid JSON responses raise ServiceError
    - Response structure is validated
    - Incorrect data types are rejected
    """

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for create_task
    # -----------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_tasks
    # -----------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for get_a_task
    # -----------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for edit_a_task
    # -----------------------------------------------------------------------------------------------------------------


    # -----------------------------------------------------------------------------------------------------------------
    # Test cases for delete_a_task
    # -----------------------------------------------------------------------------------------------------------------
