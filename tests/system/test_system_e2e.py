def response_results(response):
    return response.json()["results"]


def assert_status(response, expected_status):
    assert response.status_code == expected_status, (
        f"\nExpected status: {expected_status}"
        f"\nActual status: {response.status_code}"
        f"\nResponse body: {response.text}"
    )


def create_project(client, user_id, name="E2E Project"):
    response = client.post(
        "/projects",
        user_id=user_id,
        json={
            "name": name,
            "description": "Created by end-to-end system test.",
        },
    )

    assert_status(response, 201)
    return response_results(response)[0]


def create_time_entry(client, user_id, project_id):
    response = client.post(
        "/time-entries",
        user_id=user_id,
        json={
            "project_id": project_id,
            "description": "E2E work session.",
        },
    )

    assert_status(response, 201)
    return response_results(response)[0]


def test_services_are_available(projects_client, time_tracking_client):
    projects_response = projects_client.get("/health")
    time_tracking_response = time_tracking_client.get("/health")

    assert_status(projects_response, 200)
    assert projects_response.json() == {"status": "ok"}

    assert_status(time_tracking_response, 200)
    assert time_tracking_response.json() == {"status": "ok"}


def test_user_isolation_across_projects_service(projects_client, user_a, user_b):
    user_a_project = create_project(projects_client, user_a, name="User A Project")
    user_b_project = create_project(projects_client, user_b, name="User B Project")

    user_a_response = projects_client.get("/projects", user_id=user_a)
    user_b_response = projects_client.get("/projects", user_id=user_b)

    assert_status(user_a_response, 200)
    assert_status(user_b_response, 200)

    user_a_ids = {project["id"] for project in response_results(user_a_response)}
    user_b_ids = {project["id"] for project in response_results(user_b_response)}

    assert user_a_project["id"] in user_a_ids
    assert user_b_project["id"] not in user_a_ids

    assert user_b_project["id"] in user_b_ids
    assert user_a_project["id"] not in user_b_ids


def test_project_ownership_enforcement(projects_client, user_a, user_b):
    project = create_project(projects_client, user_a)

    detail_response = projects_client.get(f"/projects/{project['id']}", user_id=user_b)
    update_response = projects_client.patch(
        f"/projects/{project['id']}",
        user_id=user_b,
        json={"name": "Hijacked Project"},
    )
    delete_response = projects_client.delete(f"/projects/{project['id']}", user_id=user_b)

    assert_status(detail_response, 404)
    assert_status(update_response, 404)
    assert_status(delete_response, 404)

    owner_response = projects_client.get(f"/projects/{project['id']}", user_id=user_a)

    assert_status(owner_response, 200)
    assert response_results(owner_response)[0]["name"] == project["name"]


def test_cross_service_project_time_tracking_workflow(projects_client, time_tracking_client, user_a):
    project = create_project(projects_client, user_a)

    entry = create_time_entry(time_tracking_client, user_a, project["id"])

    running_response = time_tracking_client.get(
        "/time-entries",
        user_id=user_a,
        params={
            "project_id": project["id"],
            "running_only": "true",
        },
    )

    assert_status(running_response, 200)

    running_entries = response_results(running_response)

    assert len(running_entries) == 1
    assert running_entries[0]["id"] == entry["id"]
    assert running_entries[0]["project_id"] == project["id"]

    stop_response = time_tracking_client.patch(
        f"/time-entries/{entry['id']}/stop",
        user_id=user_a,
    )

    assert_status(stop_response, 200)

    stopped_entry = response_results(stop_response)[0]

    assert stopped_entry["ended_at"] is not None


def test_time_entry_user_isolation_and_ownership_enforcement(
    projects_client,
    time_tracking_client,
    user_a,
    user_b,
):
    user_a_project = create_project(projects_client, user_a, name="User A Time Project")
    user_b_project = create_project(projects_client, user_b, name="User B Time Project")

    user_a_entry = create_time_entry(time_tracking_client, user_a, user_a_project["id"])
    user_b_entry = create_time_entry(time_tracking_client, user_b, user_b_project["id"])

    user_a_list_response = time_tracking_client.get("/time-entries", user_id=user_a)
    user_b_list_response = time_tracking_client.get("/time-entries", user_id=user_b)

    assert_status(user_a_list_response, 200)
    assert_status(user_b_list_response, 200)

    user_a_entry_ids = {entry["id"] for entry in response_results(user_a_list_response)}
    user_b_entry_ids = {entry["id"] for entry in response_results(user_b_list_response)}

    assert user_a_entry["id"] in user_a_entry_ids
    assert user_b_entry["id"] not in user_a_entry_ids

    assert user_b_entry["id"] in user_b_entry_ids
    assert user_a_entry["id"] not in user_b_entry_ids

    cross_user_detail_response = time_tracking_client.get(
        f"/time-entries/{user_a_entry['id']}",
        user_id=user_b,
    )
    cross_user_delete_response = time_tracking_client.delete(
        f"/time-entries/{user_a_entry['id']}",
        user_id=user_b,
    )

    assert_status(cross_user_detail_response, 404)
    assert_status(cross_user_delete_response, 404)


def test_missing_user_context_is_rejected(projects_client, time_tracking_client):
    projects_response = projects_client.get("/projects")
    time_entries_response = time_tracking_client.get("/time-entries")

    assert_status(projects_response, 400)
    assert_status(time_entries_response, 400)