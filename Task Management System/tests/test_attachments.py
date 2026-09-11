def test_attachment_validation_and_lifecycle(client, register):
    _, headers, _ = register("Attachment User")
    task = client.post("/tasks", json={"title": "File task"}, headers=headers).json()
    bad = client.post(f"/tasks/{task['id']}/attachments", files={"file": ("bad.exe", b"bad", "application/octet-stream")}, headers=headers)
    assert bad.status_code == 400
    good = client.post(f"/tasks/{task['id']}/attachments", files={"file": ("note.txt", b"hello", "text/plain")}, headers=headers)
    assert good.status_code == 201
    attachment_id = good.json()["id"]
    assert client.get(f"/tasks/{task['id']}/attachments", headers=headers).status_code == 200
    assert client.delete(f"/attachments/{attachment_id}", headers=headers).status_code == 200


def test_attachment_size_limit_is_enforced(client, register):
    _, headers, _ = register("Large Attachment User")
    task = client.post("/tasks", json={"title": "Large file task"}, headers=headers).json()
    content = b"x" * (10 * 1024 * 1024 + 1)
    response = client.post(
        f"/tasks/{task['id']}/attachments",
        files={"file": ("large.txt", content, "text/plain")},
        headers=headers,
    )
    assert response.status_code == 413
