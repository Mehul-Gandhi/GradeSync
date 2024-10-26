from fastapi import FastAPI
# https://pypi.org/project/fullGSapi/
from fullGSapi.api import client
from dotenv import load_dotenv
import os
import json 
from utils import *

app = FastAPI()
# Load environment variables from the .env file
load_dotenv()
GRADESCOPE_EMAIL = os.getenv("EMAIL")
GRADESCOPE_PASSWORD = os.getenv("PASSWORD")
GRADESCOPE_CLIENT = client.GradescopeClient()

# Load JSON variables
config_path = os.path.join(os.path.dirname(__file__), "config.json")
with open(config_path, "r") as config_file:
    config = json.load(config_file)

# Hardcoded (for now) GradeScope CS10 Fall 2024 COURSE ID
COURSE_ID = str(config.get("COURSE_ID"))

@app.get("/")
def read_root():
    return {"message": "Welcome to the GradeSync API"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}

@app.get("/getGrades")
@handle_errors
def fetchGrades(class_id: str, assignment_id: str):
    """
    Fetches student grades from Gradescope as JSON. 

    Parameters:
        class_id (str): The ID of the class/course. If not provided, a default ID (COURSE_ID) is used.
        assignment_id (str): The ID of the assignment for which grades are to be fetched.
    Returns:
        dict or list: A list of dictionaries containing student grades if the request is successful.
                      If an error occurs, a dictionary with an error message is returned.
    Raises:
        HTTPException: If there is an issue with the request to Gradescope (e.g., network issues).
        Exception: Catches any unexpected errors and includes a descriptive message.
    """
    # If the class_id is not passed in, use the default (CS10) class id
    class_id = class_id or COURSE_ID
    try:
        GRADESCOPE_CLIENT.log_in(GRADESCOPE_EMAIL, GRADESCOPE_PASSWORD)
        filetype = "csv" # json is not supported
        GRADESCOPE_CLIENT.last_res = result = GRADESCOPE_CLIENT.session.get(f"https://www.gradescope.com/courses/{class_id}/assignments/{assignment_id}/scores.{filetype}")
        if result.ok:
            csv_content = result.content.decode("utf-8")
            json_content = csv_to_json(csv_content)
            return json_content
        else:
            return {"message": f"Failed to fetch grades: {result.status_code}. "}
    except Exception as e:
        return {"message": "Unknown error " + str(e)}
    finally:
        # Ensure logout
        try:
            GRADESCOPE_CLIENT.logout()
        except Exception as e:
            print(f"Logout failed: {e}")
