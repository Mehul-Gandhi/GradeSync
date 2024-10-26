from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_fetch_grades():
    response = client.get("/getGrades", params={"class_id": "902165", "assignment_id": "5211665"})
    print(response.content)
    assert response.status_code == 200
    assert "message" not in response.json()  # Assuming success response does not include an error message
