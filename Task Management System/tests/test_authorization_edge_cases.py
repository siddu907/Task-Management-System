def test_users_cannot_access_other_users_tasks(client, register):
    _, owner_headers, _ = register("Task Owner")
    _, other_headers, _ = register("Unrelated User")
    task = client.post("/tasks", json={"title": "Private task"}, headers=owner_headers).json()
    assert client.get(f"/tasks/{task['id']}", headers=other_headers).status_code == 403
    assert client.put(f"/tasks/{task['id']}", json={"title": "Tampered"}, headers=other_headers).status_code == 403
    assert client.delete(f"/tasks/{task['id']}", headers=other_headers).status_code == 403


def test_assignee_can_only_change_status_and_priority(client, register):
    owner, owner_headers, _ = register("Owner")
    assignee, assignee_headers, _ = register("Assignee")
    task = client.post("/tasks", json={"title": "Assigned"}, headers=owner_headers).json()
    assert client.put(f"/tasks/{task['id']}/assign", json={"assigned_to_id": assignee["id"]}, headers=owner_headers).status_code == 200
    assert client.put(f"/tasks/{task['id']}/assign", json={"assigned_to_id": assignee["id"]}, headers=assignee_headers).status_code == 403
    assert client.put(f"/tasks/{task['id']}", json={"assigned_to_id": owner["id"]}, headers=assignee_headers).status_code == 422
    assert client.put(f"/tasks/{task['id']}", json={"description": "Not allowed"}, headers=assignee_headers).status_code == 403
    assert client.put(f"/tasks/{task['id']}/priority", json={"priority": "high"}, headers=assignee_headers).status_code == 200


def test_admin_can_manage_other_users_comments(client, admin, register):
    _, admin_headers = admin
    _, owner_headers, _ = register("Comment Owner")
    task = client.post("/tasks", json={"title": "Admin comment"}, headers=owner_headers).json()
    comment = client.post(f"/tasks/{task['id']}/comments", json={"content": "Original"}, headers=owner_headers).json()
    assert client.put(f"/comments/{comment['id']}", json={"content": "Admin edit"}, headers=admin_headers).status_code == 200
    assert client.delete(f"/comments/{comment['id']}", headers=admin_headers).status_code == 200


def test_unknown_resources_return_not_found(client, register):
    _, headers, _ = register("Not Found User")
    assert client.get("/tasks/999999999", headers=headers).status_code == 404
    assert client.get("/tasks/999999999/comments", headers=headers).status_code == 404
    assert client.get("/notifications/999999999/read", headers=headers).status_code in {405, 404}
