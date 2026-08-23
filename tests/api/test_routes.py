"""Unit tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from app.api.server import create_app

client = TestClient(create_app())


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "OraCLI" in data["app_name"]


def test_api_sql_lifecycle():
    # 1. Reset database
    client.post("/api/database/reset")

    # 2. CREATE TABLE
    create_sql = """
    CREATE TABLE student (
        rollno NUMBER,
        name VARCHAR2(50),
        cgpa NUMBER(3,2)
    );
    """
    res = client.post("/api/sql/execute", json={"sql": create_sql})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "Table created." in data["combined_formatted_output"]

    # 3. INSERT
    insert_sql = "INSERT INTO student VALUES (101, 'Rahul', 8.7);"
    res = client.post("/api/sql/execute", json={"sql": insert_sql})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "1 row created." in data["combined_formatted_output"]

    # 4. SELECT
    select_sql = "SELECT * FROM student;"
    res = client.post("/api/sql/execute", json={"sql": select_sql})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "ROLLNO" in data["combined_formatted_output"]
    assert "Rahul" in data["combined_formatted_output"]
    assert "1 row selected." in data["combined_formatted_output"]

    # 5. Schema tables endpoint
    res_schema = client.get("/api/schema/tables")
    assert res_schema.status_code == 200
    schema_data = res_schema.json()
    table_names = [t["table_name"] for t in schema_data["tables"]]
    assert "student" in table_names


def test_api_sql_error():
    res = client.post("/api/sql/execute", json={"sql": "SELECT * FROM nonexistent_table;"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is False
    assert "ORA-00942" in data["combined_formatted_output"]
