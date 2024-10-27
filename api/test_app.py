from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_fetch_grades():
    response = client.get("/getGrades", params={"class_id": "902165", "assignment_id": "5211665"})
    print(response.content)
    assert response.status_code == 200
    assert "message" not in response.json()  # Assuming success response does not include an error message

def test_lab_conceptual():
    response = client.get("/getGradeScopeAssignmentID/labs/2", params={"lab_type": 1})
    print(response.content)
    assert response.status_code == 200
    assert "assignment_id" in response.json()  # Verifies if assignment_id is in response

def test_lecture_quiz():
    response = client.get("/getGradeScopeAssignmentID/lecture_quizzes/3")
    print(response.content)
    assert response.status_code == 200
    assert "assignment_id" in response.json()  # Verifies if assignment_id is in response

def test_lab_code():
    response = client.get("/getGradeScopeAssignmentID/labs/2", params={"lab_type": 0})
    print(response.content)
    assert response.status_code == 200
    assert "assignment_id" in response.json()  # Verifies if assignment_id is in response

def test_discussion():
    response = client.get("/getGradeScopeAssignmentID/discussions/1")
    print(response.content)
    assert response.status_code == 200
    assert "assignment_id" in response.json()  # Verifies if assignment_id is in response
    