def test_task_crud_assignment_and_status_rules(client, register):
    creator, creator_headers, _ = register("Creator")
    assignee, assignee_headers, _ = register("Assignee")
    response = client.post("/tasks", json={"title": "Lifecycle", "priority": "critical"}, headers=creator_headers)
    assert response.status_code == 201
    task_id = response.json()["id"]
    assignment = client.put(f"/tasks/{task_id}/assign", json={"assigned_to_id": assignee["id"]}, headers=creator_headers)
    assert assignment.status_code == 200
    assert assignment.json()["message"] == f"Task ID {task_id} assigned to user ID {assignee['id']}"
    assert client.get(f"/tasks/{task_id}", headers=assignee_headers).status_code == 200
    same_assignment = client.put(f"/tasks/{task_id}/assign", json={"assigned_to_id": assignee["id"]}, headers=creator_headers)
    assert same_assignment.status_code == 200
    assert same_assignment.json()["message"] == f"Task ID {task_id} is already assigned to user ID {assignee['id']}"
    reassignment = client.put(f"/tasks/{task_id}/assign", json={"assigned_to_id": creator["id"]}, headers=creator_headers)
    assert reassignment.status_code == 200
    assert reassignment.json()["message"] == f"Task ID {task_id} reassigned from user ID {assignee['id']} to user ID {creator['id']}"
    assert client.put(f"/tasks/{task_id}/status?status=in_progress", headers=creator_headers).status_code == 200
    assert client.put(f"/tasks/{task_id}/status?status=completed", headers=creator_headers).status_code == 200
    assert client.put(f"/tasks/{task_id}", json={"title": "Cannot change"}, headers=creator_headers).status_code == 400
    assert client.delete(f"/tasks/{task_id}", headers=creator_headers).status_code == 200


def test_task_search_filter_sort_and_pagination(client, register):
    _, headers, _ = register("Search User")
    client.post("/tasks", json={"title": "Payment report", "priority": "high"}, headers=headers)
    response = client.get("/tasks?search=payment&status=todo&page=1&limit=1&sort_by=title&sort_order=asc", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) <= 1


def test_every_invalid_status_transition_is_rejected(client, register):
    _, headers, _ = register("Transition User")
    task = client.post("/tasks", json={"title": "Transition matrix"}, headers=headers).json()
    task_id = task["id"]
    assert client.put(f"/tasks/{task_id}/status?status=completed", headers=headers).status_code == 400
    assert client.put(f"/tasks/{task_id}/status?status=cancelled", headers=headers).status_code == 200
    assert client.put(f"/tasks/{task_id}/status?status=completed", headers=headers).status_code == 400

    second = client.post("/tasks", json={"title": "Completion matrix"}, headers=headers).json()
    second_id = second["id"]
    assert client.put(f"/tasks/{second_id}/status?status=in_progress", headers=headers).status_code == 200
    completed = client.put(f"/tasks/{second_id}/status?status=completed", headers=headers)
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None
    assert client.put(f"/tasks/{second_id}/status?status=todo", headers=headers).status_code == 400
    assert client.put(f"/tasks/{second_id}/status?status=in_progress", headers=headers).status_code == 400
