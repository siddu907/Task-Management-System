def test_comment_crud_and_ownership(client, register):
    _, owner_headers, _ = register("Comment Owner")
    _, other_headers, _ = register("Other User")
    task = client.post("/tasks", json={"title": "Comment task"}, headers=owner_headers).json()
    comment = client.post(f"/tasks/{task['id']}/comments", json={"content": "Initial"}, headers=owner_headers)
    assert comment.status_code == 201
    comment_id = comment.json()["id"]
    assert client.get(f"/tasks/{task['id']}/comments", headers=owner_headers).status_code == 200
    assert client.put(f"/comments/{comment_id}", json={"content": "Changed"}, headers=other_headers).status_code == 403
    assert client.put(f"/comments/{comment_id}", json={"content": "Changed"}, headers=owner_headers).status_code == 200
    assert client.delete(f"/comments/{comment_id}", headers=owner_headers).status_code == 200
