# README

### 1. Environment Setup
- Store GradeScope credentials in environment variables `EMAIL` and `PASSWORD`. These can be defined inside a `.env` file.

### 2. Google Authentication
- Follow the steps at the following link to enable Google authentication: `"https://developers.google.com/sheets/api/quickstart/python#authorize_credentials_for_a_desktop_application"`

### 3. Set Constants as Necessary

- **COURSE_ID**: The course ID is the final component of the URL on the GradeScope course homepage: `https://www.gradescope.com/courses/[COURSE_ID]`

- **SCOPES**: This should not be modified by the user. Use `"https://www.googleapis.com/auth/spreadsheets"` to allow write access.

- **SPREADSHEET_ID**: The spreadsheet ID is the final component of the spreadsheet’s URL: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit?gid=0#gid=0`

- **NUMBER_OF_STUDENTS**: The number of students enrolled in the course.

- **UNGRADED_LABS**: Some labs are not included in the final grade calculation. `UNGRADED_LABS` is a list of such labs. For example, if labs 5 and 6 are not included, set `UNGRADED_LABS` to `[5, 6]`.

- **TOTAL_LAB_POINTS**: Used only for the final grade calculation; this is the total number of lab points in a semester.

- **NUM_LECTURES**: Used only for the final lecture-quiz grade calculation.

- **SPECIAL_CASE_LABS**: A list of 4-part labs (lab assignments with four dropboxes, instead of the typical one or two).

- **NUM_LECTURE_DROPS**: The number of drops included in the lecture-quiz grade calculation.
