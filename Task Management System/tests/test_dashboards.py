def test_user_dashboard(client, register):
    _, headers, _ = register("Dashboard User")
    client.post("/tasks", json={"title": "Dashboard task", "priority": "critical"}, headers=headers)
    response = client.get("/dashboard/user", headers=headers)
    assert response.status_code == 200
    assert response.json()["my_tasks"] >= 1


def test_admin_dashboard_and_audit_logs(client, admin):
    _, headers = admin
    dashboard = client.get("/dashboard/admin", headers=headers)
    assert dashboard.status_code == 200
    assert "total_users" in dashboard.json()
    assert client.get("/audit-logs", headers=headers).status_code == 200


def test_user_dashboard_counts_overdue_and_critical_tasks(client, register):
    _, headers, _ = register("Overdue Dashboard User")
    client.post(
        "/tasks",
        json={"title": "Overdue critical", "priority": "critical", "due_date": "2020-01-01T00:00:00"},
        headers=headers,
    )
    response = client.get("/dashboard/user", headers=headers)
    assert response.status_code == 200
    assert response.json()["overdue_tasks"] >= 1
    assert response.json()["critical_tasks"] >= 1
