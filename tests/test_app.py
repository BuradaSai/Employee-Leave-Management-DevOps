
import pytest
from datetime import date, timedelta
import app as application


@pytest.fixture
def client(tmp_path):
    application.app.config["TESTING"] = True
    application.app.config["SECRET_KEY"] = "test-secret"

    application.DATABASE = tmp_path / "test_leave.db"
    application.init_db()

    with application.app.test_client() as test_client:
        yield test_client


def login(client, username, password):
    return client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


def test_employee_login(client):
    response = login(client, "employee1", "emp1123")
    assert response.status_code == 200
    assert b"Welcome, employee1" in response.data


def test_manager_login(client):
    response = login(client, "manager", "mgr123")
    assert response.status_code == 200
    assert b"Welcome, manager" in response.data


def test_invalid_login(client):
    response = login(client, "unknown", "wrong")
    assert b"Invalid username or password" in response.data


def test_employee_can_apply_for_leave(client):
    login(client, "employee1", "emp1123")

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    response = client.post(
        "/apply",
        data={
            "leave_type": "Casual",
            "start_date": tomorrow,
            "end_date": tomorrow,
            "reason": "Personal work",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Leave request submitted successfully" in response.data
    assert b"Pending" in response.data


def test_manager_can_approve_leave(client):
    login(client, "employee1", "emp1123")

    tomorrow = (date.today() + timedelta(days=1)).isoformat()

    client.post(
        "/apply",
        data={
            "leave_type": "Casual",
            "start_date": tomorrow,
            "end_date": tomorrow,
            "reason": "Personal work",
        },
    )

    client.get("/logout")
    login(client, "manager", "mgr123")

    response = client.post(
        "/leave/1/approve",
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Approved" in response.data


def test_employee_cannot_approve_leave(client):
    login(client, "employee1", "emp1123")

    response = client.post("/leave/1/approve", follow_redirects=True)

    assert b"not authorized" in response.data.lower()
