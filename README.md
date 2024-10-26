# GradeSync

### About

GradeSync is a backend microservice that integrates with assessment platforms to fetch student grades and facilitate management of post-semester submissions. GradeSync enables students to submit coursework after the term ends and view their updated grades on the GradeView dashboard. GradeSync automates gradebook updates, eliminating the need for manual instructor intervention.

### Pre-setup 
1. Download the Docker Desktop application
2. In the terminal, run `docker --version` to ensure Docker is correctly installed.
### How to Launch the App

1. Open the Docker desktop application.
2. In the terminal, navigate to the `/api` directory of this project.
3. Build the Docker image using `docker-compose build`.
4. Start the application with `docker-compose start` (or `docker-compose up` to view console output).
5. Confirm the application is running by opening [http://localhost:8000/](http://localhost:8000/) on a browser.
6. Test endpoints with a tool like ThunderClient or Postman.
- Go to VSCode extensions, and add "ThunderClient" to your extensions.
- Click "New Request" to test the API endpoints.
7. When you are finished, run `docker-compose down` or press CTRL+C to stop the server.
