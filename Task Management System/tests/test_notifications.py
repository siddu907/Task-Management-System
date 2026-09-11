def test_notification_read_flows(client, register):
    _, owner_headers, _ = register("Notification Owner")
    assignee, assignee_headers, _ = register("Notification Assignee")
    task = client.post("/tasks", json={"title": "Notify"}, headers=owner_headers).json()
    assert client.put(f"/tasks/{task['id']}/assign", json={"assigned_to_id": assignee["id"]}, headers=owner_headers).status_code == 200
    notifications = client.get("/notifications", headers=assignee_headers).json()
    assert notifications
    notification_id = notifications[0]["id"]
    assert client.put(f"/notifications/{notification_id}/read", headers=assignee_headers).status_code == 200
    assert client.put("/notifications/read-all", headers=assignee_headers).status_code == 200
    assert client.get(f"/tasks/{task['id']}", headers=owner_headers).status_code == 200


def test_assignment_reassignment_status_completion_and_comment_notifications(client, register):
    owner, owner_headers, _ = register("Event Owner")
    first_assignee, first_headers, _ = register("First Assignee")
    second_assignee, second_headers, _ = register("Second Assignee")
    task = client.post("/tasks", json={"title": "Notification Events"}, headers=owner_headers).json()

    assigned = client.put(f"/tasks/{task['id']}/assign", json={"assigned_to_id": first_assignee["id"]}, headers=owner_headers)
    assert assigned.status_code == 200
    assert any(item["notification_type"] == "task_assigned" for item in client.get("/notifications", headers=first_headers).json())

    reassigned = client.put(f"/tasks/{task['id']}/assign", json={"assigned_to_id": second_assignee["id"]}, headers=owner_headers)
    assert reassigned.status_code == 200
    assert any(item["notification_type"] == "task_reassigned" for item in client.get("/notifications", headers=first_headers).json())
    assert any(item["notification_type"] == "task_reassigned" for item in client.get("/notifications", headers=second_headers).json())

    assert client.put(f"/tasks/{task['id']}/status?status=in_progress", headers=owner_headers).status_code == 200
    assert any(item["notification_type"] == "status_changed" for item in client.get("/notifications", headers=second_headers).json())
    assert client.post(f"/tasks/{task['id']}/comments", json={"content": "Progress update"}, headers=second_headers).status_code == 201
    assert any(item["notification_type"] == "comment_added" for item in client.get("/notifications", headers=owner_headers).json())
    assert client.put(f"/tasks/{task['id']}/status?status=completed", headers=owner_headers).status_code == 200
    assert any(item["notification_type"] == "task_completed" for item in client.get("/notifications", headers=second_headers).json())


def test_notifications_are_isolated_between_users(client, register):
    _, owner_headers, _ = register("Notification Owner Two")
    assignee, assignee_headers, _ = register("Notification Assignee Two")
    _, unrelated_headers, _ = register("Unrelated Notification User")
    task = client.post("/tasks", json={"title": "Private notification"}, headers=owner_headers).json()
    assert client.put(f"/tasks/{task['id']}/assign", json={"assigned_to_id": assignee["id"]}, headers=owner_headers).status_code == 200
    assert client.get("/notifications", headers=assignee_headers).json()
    assert client.get("/notifications", headers=unrelated_headers).json() == []
