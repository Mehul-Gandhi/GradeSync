# Author: Naveen Nathan

import json

from fullGSapi.api import client as GradescopeClient
import os.path
import re
import io
import time
import warnings
import functools
from googleapiclient.errors import HttpError
import gspread
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import backoff
# Uncomment below import if you would like to use the spreadsheet dash functionality in populate_instructor_dashboard
#import pandas as pd


load_dotenv()
GRADESCOPE_EMAIL = os.getenv("GRADESCOPE_EMAIL")
GRADESCOPE_PASSWORD = os.getenv("GRADESCOPE_PASSWORD")
import logging
import sys

# Configure logging to output to both file and console
logging.basicConfig(
    level=logging.INFO,  # or DEBUG for more detail
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        #logging.FileHandler("/var/log/cron.log"),  # Logs to file
        logging.StreamHandler(sys.stdout)  # Logs to console (stdout)
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting the gradescope_to_spreadsheet script.")

# Load JSON variables
class_json_name = 'cs10_fall2024.json'
config_path = os.path.join(os.path.dirname(__file__), 'config/', class_json_name)
with open(config_path, "r") as config_file:
    config = json.load(config_file)

# IDs to link files
COURSE_ID = config["COURSE_ID"]
SCOPES = config["SCOPES"]
SPREADSHEET_ID = config["SPREADSHEET_ID"]

# Course metadata
NUMBER_OF_STUDENTS = config["NUMBER_OF_STUDENTS"]
NUM_LECTURE_DROPS = config["NUM_LECTURE_DROPS"]

# Lab number of labs that are not graded.
UNGRADED_LABS = config["UNGRADED_LABS"]

# Used only for Final grade calculation; not for display in the middle of the semester
TOTAL_LAB_POINTS = config["TOTAL_LAB_POINTS"]
NUM_LECTURES = config["NUM_LECTURES"]

# Used for labs with 4 parts (very uncommon)
SPECIAL_CASE_LABS = config["SPECIAL_CASE_LABS"]

# The ASSIGNMENT_ID constant is for users who wish to generate a sub-sheet (not update the dashboard) for one assignment, passing it as a parameter.
ASSIGNMENT_ID = (len(sys.argv) > 1) and sys.argv[1]
ASSIGNMENT_NAME = (len(sys.argv) > 2) and sys.argv[2]


# This is not a constant; it is a variable that needs global scope. It should not be modified by the user
subsheet_titles_to_ids = None
# Tracking the number of_attempts to_update a sheet.
number_of_retries_needed_to_update_sheet = 0

def deprecated(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        warnings.warn(
            f"'{func.__name__}' is deprecated and will be removed in a future version.",
            DeprecationWarning,
            stacklevel=2
        )
        return func(*args, **kwargs)
    return wrapper

credentials_json = os.getenv("SERVICE_ACCOUNT_CREDENTIALS")
credentials_dict = json.loads(credentials_json)
credentials = Credentials.from_service_account_info(credentials_dict, scopes=SCOPES)
client = gspread.authorize(credentials)

def writeToSheet(sheet_api_instance, assignment_scores, assignment_name = ASSIGNMENT_NAME):
    global number_of_retries_needed_to_update_sheet
    try:
        sub_sheet_titles_to_ids = get_sub_sheet_titles_to_ids(sheet_api_instance)

        sheet_id = None

        if assignment_name not in sub_sheet_titles_to_ids:
            create_sheet_rest_request = {
                "requests": {
                    "addSheet": {
                        "properties": {
                            "title": assignment_name
                        }
                    }
                }
            }
            request = sheet_api_instance.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=create_sheet_rest_request)
            response = make_request(request)
            sheet_id = response['replies'][0]['addSheet']['properties']['sheetId']
        else:
            sheet_id = sub_sheet_titles_to_ids[assignment_name]
        update_sheet_with_csv(assignment_scores, sheet_api_instance, sheet_id)
        logger.info(f"Successfully updated spreadsheet with: {assignment_name} after {number_of_retries_needed_to_update_sheet} retries")
        number_of_retries_needed_to_update_sheet = 0
    except HttpError as err:
        logger.error(err)
except Exception as err:
    logger.error(f"An unknown error has occurred: {err}")
def create_sheet_api_instance():
    service = build("sheets", "v4", credentials=credentials)
    sheet_api_instance = service.spreadsheets()
    return sheet_api_instance


def get_sub_sheet_titles_to_ids(sheet_api_instance):
    global subsheet_titles_to_ids
    if subsheet_titles_to_ids:
        return subsheet_titles_to_ids
    logger.info("Retrieving subsheet titles to ids")
    request = sheet_api_instance.get(spreadsheetId=SPREADSHEET_ID, fields='sheets/properties')
    sheets = request.execute()
    subsheet_titles_to_ids = {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in
                               sheets['sheets']}
    return subsheet_titles_to_ids

def is_429_error(exception):
    return isinstance(exception, HttpError) and exception.resp.status == 429
def backoff_handler():
    global number_of_retries_needed_to_update_sheet
    number_of_retries_needed_to_update_sheet += 1
    pass
@backoff.on_exception(
    backoff.expo,
    Exception,
    max_tries=5,
    on_backoff=backoff_handler,
    giveup=lambda e: not is_429_error(e)
)
def make_request(request):
    return request.execute()

def update_sheet_with_csv(assignment_scores, sheet_api_instance, sheet_id, rowIndex = 0, columnIndex=0):
    push_grade_data_rest_request = {
        'requests': [
            {
                'pasteData': {
                    "coordinate": {
                        "sheetId": sheet_id,
                        "rowIndex": rowIndex,
                        "columnIndex": columnIndex,
                    },
                    "data": assignment_scores,
                    "type": 'PASTE_NORMAL',
                    "delimiter": ',',
                }
            }
        ]
    }
    request = sheet_api_instance.batchUpdate(spreadsheetId=SPREADSHEET_ID, body=push_grade_data_rest_request)
    make_request(request)


def retrieve_grades_from_gradescope(gradescope_client, assignment_id = ASSIGNMENT_ID):
    assignment_scores = str(gradescope_client.download_scores(COURSE_ID, assignment_id)).replace("\\n", "\n")
    return assignment_scores


def initialize_gs_client():
    gradescope_client = GradescopeClient.GradescopeClient()
    gradescope_client.log_in(GRADESCOPE_EMAIL, GRADESCOPE_PASSWORD)
    return gradescope_client


def get_assignment_info(gs_instance, class_id: str) -> bytes:
    if not gs_instance.logged_in:
        logger.error("You must be logged in to download grades!")
        return False
    gs_instance.last_res = res = gs_instance.session.get(f"https://www.gradescope.com/courses/{class_id}/assignments")
    if not res or not res.ok:
        logger.error(f"Failed to get a response from gradescope! Got: {res}")
        return False
    return res.content


def make_score_sheet_for_one_assignment(sheet_api_instance, gradescope_client, assignment_name = ASSIGNMENT_NAME,
                                        assignment_id=ASSIGNMENT_ID):
    assignment_scores = retrieve_grades_from_gradescope(gradescope_client = gradescope_client, assignment_id = assignment_id)
    writeToSheet(sheet_api_instance, assignment_scores, assignment_name)
    return assignment_scores

"""
This method returns a dictionary mapping assignment IDs to the names (titles) of the assignments
"""

def get_assignment_id_to_names(gradescope_client):
    # The response cannot be parsed as a json as is.
    course_info_response = str(get_assignment_info(gradescope_client, COURSE_ID)).replace("\\", "").replace("\\u0026", "&")
    pattern = '{"id":[0-9]+,"title":"[^}"]+?"}'
    info_for_all_assignments = re.findall(pattern, course_info_response)
    assignment_to_names = {}
    #  = { json.loads(assignment)['id'] : json.loads(assignment)['title'] for assignment in info_for_all_assignments }
    for assignment in info_for_all_assignments:
        assignment_as_json = json.loads(assignment)
        assignment_to_names[str(assignment_as_json["id"])] = assignment_as_json["title"]
    return assignment_to_names

def main():
    start_time = time.time()
    if len(sys.argv) > 1:
        gradescope_client = initialize_gs_client()
        make_score_sheet_for_one_assignment(credentials, gradescope_client=gradescope_client,
                                            assignment_name=ASSIGNMENT_NAME, assignment_id=ASSIGNMENT_ID)
    else:
        push_all_grade_data_to_sheets()
    end_time = time.time()
    logger.info(f"Finished in {round(end_time - start_time, 2)} seconds")

def push_all_grade_data_to_sheets():
    gradescope_client = initialize_gs_client()
    assignment_id_to_names = get_assignment_id_to_names(gradescope_client)
    # The below code is used to filter assignments by category when populating the instructor dashboard
    """
    labs = filter(lambda assignment: "lab" in assignment.lower(),
                  assignment_id_to_names.values())
    extract_number_from_lab_title = lambda lab: int(re.findall("\d+", lab)[0])
    sorted_labs = sorted(labs, key=extract_number_from_lab_title)

    assignment_names_to_ids = {v: k for k, v in assignment_id_to_names.items()}
    projects = set(filter(lambda assignment: "project" in assignment.lower(),
                  assignment_id_to_names.values()))
    sorted_projects = sorted(projects, key=lambda project: assignment_names_to_ids[project])

    lecture_quizzes = list(filter(lambda assignment: "lecture" in assignment.lower(),
                  assignment_id_to_names.values()))

    discussions = filter(lambda assignment: "discussion" in assignment.lower(),
                  assignment_id_to_names.values())
    """
    sheet_api_instance = create_sheet_api_instance()

    all_lab_ids = set()
    paired_lab_ids = set()

    # An assignment is marked as current if there are >3 submissions and if the commented code in the for loop below is removed
    assignment_id_to_currency_status = {}
    for id in assignment_id_to_names:
        assignment_scores = make_score_sheet_for_one_assignment(sheet_api_instance, gradescope_client=gradescope_client,
                                                                assignment_name=assignment_id_to_names[id], assignment_id=id)
        #if assignment_scores.count("Graded") >= 3:
        #    assignment_id_to_currency_status[id] = assignment_scores


# Need to import pandas if you would like to use this function.
def populate_instructor_dashboard(all_lab_ids, assignment_id_to_currency_status, assignment_id_to_names,
                                  assignment_names_to_ids, dashboard_dict, dashboard_sheet_id, discussions,
                                  extract_number_from_lab_title, id, lecture_quizzes, paired_lab_ids,
                                  sheet_api_instance, sorted_labs, sorted_projects):
    for i in range(len(sorted_labs) - 1):
        first_element = sorted_labs[i]
        second_element = sorted_labs[i + 1]
        first_element_assignment_id = assignment_names_to_ids[first_element]
        second_element_assignment_id = assignment_names_to_ids[second_element]
        first_element_lab_number = extract_number_from_lab_title(first_element)
        second_element_lab_number = extract_number_from_lab_title(second_element)
        if first_element_lab_number in UNGRADED_LABS:
            continue
        all_lab_ids.add(first_element_assignment_id)
        all_lab_ids.add(second_element_assignment_id)
        if first_element_lab_number == second_element_lab_number:
            paired_lab_ids.add(first_element_assignment_id)
            paired_lab_ids.add(second_element_assignment_id)
            if first_element_lab_number in SPECIAL_CASE_LABS:
                continue
            if assignment_id_to_currency_status[id]:
                spreadsheet_query = f"=DIVIDE(XLOOKUP(C:C, {first_element_assignment_id}!C:C, {first_element_assignment_id}!E:E) + XLOOKUP(C:C, {second_element_assignment_id}!C:C, {second_element_assignment_id}!E:E), XLOOKUP(C:C, {first_element_assignment_id}!C:C, {first_element_assignment_id}!F:F) + XLOOKUP(C:C, {second_element_assignment_id}!C:C, {second_element_assignment_id}!F:F))"
                dashboard_dict["Lab " + str(first_element_lab_number)] = [spreadsheet_query] * NUMBER_OF_STUDENTS
    unpaired_lab_ids = all_lab_ids - paired_lab_ids
    for lab_id in unpaired_lab_ids:
        if assignment_id_to_currency_status[id]:
            spreadsheet_query = f"=DIVIDE(XLOOKUP(C:C, {lab_id}!C:C, {lab_id}!E:E), XLOOKUP(C:C, {lab_id}!C:C, {lab_id}!F:F))"
            lab_number = extract_number_from_lab_title(assignment_id_to_names[lab_id])
            dashboard_dict["Lab " + str(lab_number)] = [spreadsheet_query] * NUMBER_OF_STUDENTS
    for lab_number in SPECIAL_CASE_LABS:
        if assignment_id_to_currency_status[id]:
            special_case_lab_name = "Lab " + str(lab_number)
            special_lab_ids = []
            for lab_name in sorted_labs:
                if special_case_lab_name in lab_name:
                    special_lab_ids.append(assignment_names_to_ids[lab_name])
            spreadsheet_query = f"=DIVIDE(XLOOKUP(C:C, {special_lab_ids[0]}!C:C, {special_lab_ids[0]}!E:E) + XLOOKUP(C:C, {special_lab_ids[1]}!C:C, {special_lab_ids[1]}!E:E) + XLOOKUP(C:C, {special_lab_ids[2]}!C:C, {special_lab_ids[2]}!E:E) + XLOOKUP(C:C, {special_lab_ids[3]}!C:C, {special_lab_ids[3]}!E:E), XLOOKUP(C:C, {special_lab_ids[0]}!C:C, {special_lab_ids[0]}!F:F) + XLOOKUP(C:C, {special_lab_ids[1]}!C:C, {special_lab_ids[1]}!F:F) + XLOOKUP(C:C, {special_lab_ids[2]}!C:C, {special_lab_ids[2]}!F:F) + XLOOKUP(C:C, {special_lab_ids[3]}!C:C, {special_lab_ids[3]}!F:F))"
            dashboard_dict[special_case_lab_name] = [spreadsheet_query] * NUMBER_OF_STUDENTS
    num_graded_labs = len(dashboard_dict) - len(UNGRADED_LABS)
    lab_score_column = [
        f"=ARRAYFORMULA(COUNTIF(FILTER(I{i + 2}:{i + 2}, REGEXMATCH(I1:1, \"Lab\")), 1) / {num_graded_labs} * {TOTAL_LAB_POINTS})"
        for i in range(NUMBER_OF_STUDENTS)]
    lab_score_title = "Su24CS10 Final Lab Score / 100"
    lab_score_dict = {lab_score_title: lab_score_column}
    number_of_full_credit_labs = [f"=ARRAYFORMULA(COUNTIF(FILTER(I{i + 2}:{i + 2}, REGEXMATCH(I1:1, \"Lab\")), 1))" for
                                  i in range(NUMBER_OF_STUDENTS)]
    number_of_full_credit_labs_dict = {"# of full credit labs": number_of_full_credit_labs}
    lab_average_column = [f"=ARRAYFORMULA(AVERAGE(FILTER(I{i + 2}:{i + 2}, REGEXMATCH(I1:1, \"Lab\"))))" for i in
                          range(NUMBER_OF_STUDENTS)]
    lab_average_dict = {"Avg. Lab Score": lab_average_column}
    project_average_column = [f"=ARRAYFORMULA(AVERAGE(FILTER(J{i + 2}:{i + 2}, REGEXMATCH(J1:1, \"Project\"))))" for i
                              in range(NUMBER_OF_STUDENTS)]
    project_average_dict = {"Avg. Project Score": project_average_column}
    lecture_attendance_score = [
        f"=ARRAYFORMULA((COUNTIF(FILTER(I{i + 2}:{i + 2}, REGEXMATCH(I1:1, \"Lecture\")), 1) + {NUM_LECTURE_DROPS}) / {len(lecture_quizzes)})"
        for i in range(NUMBER_OF_STUDENTS)]
    lecture_quiz_count_dict = {"Su24CS10 Final Lecture Attendance Score (Drops Included)": lecture_attendance_score}
    discussion_makeup_count = [f"=ARRAYFORMULA(COUNTIF(FILTER(I{i + 2}:{i + 2}, REGEXMATCH(I1:1, \"Discussion\")), 1))"
                               for i in range(NUMBER_OF_STUDENTS)]
    discussion_makeup_count_dict = {"Su24CS10 Number of Discussion Makeups": discussion_makeup_count}
    for assignment_name in sorted_projects:
        if assignment_id_to_currency_status[id]:
            assignment_id = assignment_names_to_ids[assignment_name]
            spreadsheet_query = f"=DIVIDE(XLOOKUP(C:C, {assignment_id}!C:C, {assignment_id}!E:E), XLOOKUP(C:C, {assignment_id}!C:C, {assignment_id}!F:F))"
            dashboard_dict[assignment_name] = [spreadsheet_query] * NUMBER_OF_STUDENTS
    for assignment_name in lecture_quizzes:
        if assignment_id_to_currency_status[id]:
            assignment_id = assignment_names_to_ids[assignment_name]
            spreadsheet_query = f"=DIVIDE(XLOOKUP(C:C, {assignment_id}!C:C, {assignment_id}!E:E), XLOOKUP(C:C, {assignment_id}!C:C, {assignment_id}!F:F))"
            dashboard_dict[assignment_name] = [spreadsheet_query] * NUMBER_OF_STUDENTS
    for assignment_name in discussions:
        if assignment_id_to_currency_status[id]:
            assignment_id = assignment_names_to_ids[assignment_name]
            spreadsheet_query = f"=IF(XLOOKUP(C:C, {assignment_id}!C:C, {assignment_id}!G:G) <> \"Missing\", 1, 0)"
            dashboard_dict[assignment_name] = [spreadsheet_query] * NUMBER_OF_STUDENTS
    dashboard_dict_with_aggregate_columns = {}
    dashboard_dict_with_aggregate_columns.update(lab_score_dict)
    dashboard_dict_with_aggregate_columns.update(lecture_quiz_count_dict)
    dashboard_dict_with_aggregate_columns.update(discussion_makeup_count_dict)
    dashboard_dict_with_aggregate_columns.update(number_of_full_credit_labs_dict)
    dashboard_dict_with_aggregate_columns.update(lab_average_dict)
    dashboard_dict_with_aggregate_columns.update(project_average_dict)
    dashboard_dict_with_aggregate_columns.update(dashboard_dict)
    first_column_name = lab_score_title
    dashboard_df = pd.DataFrame(dashboard_dict_with_aggregate_columns).set_index(first_column_name)
    output = io.StringIO()
    dashboard_df.to_csv(output)
    update_sheet_with_csv(output.getvalue(), sheet_api_instance, dashboard_sheet_id, 0, 3)
    output.close()


if __name__ == "__main__":
    main()
