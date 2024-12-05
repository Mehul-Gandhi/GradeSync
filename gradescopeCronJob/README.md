# README

### Requirements  

- **Gradescope Access**: Teaching Assistant or Instructor role on a CS10 Gradescope course instance.  
- **Google Cloud Project**: Configured for Google Sheets API access. 


### 1. Environment Setup

- Store Gradescope credentials in environment variables `GRADESCOPE_EMAIL` and `GRADESCOPE_PASSWORD`. Define these in a `.env` file.
- If you do not have a password setup on Gradescope, you will need to create a password.
- There should be three variables total in the `.env` file. Follow step 2 to add the `SERVICE_ACCOUNT_CREDENTIALS` variable.


### 2. Google Authentication Setup

1. **Create a New Project in Google Cloud Console**
   - Go to [Google Cloud Console](https://console.cloud.google.com/).
   - In the top-left corner, create a new project.

2. **Enable Google Sheets API**
   - Select your project and navigate to **APIs & Services**.
   - Go to the **Library** tab and search for "Google Sheets API".
   - Click on **Google Sheets API** and enable it.

3. **Create a Service Account**
   - Go to the **Credentials** tab within **APIs & Services**.
   - Fill out the fields as necessary to create a new service account.
   - No additional roles are required at this stage.

4. **Share Google Sheets Access**
   - Under the **Service Accounts** section on the **Credentials** page, click on the account email.
   - Share the Google Sheet with this email address to give access.
   - If this step is skipped, you will get a 403 Access Forbidden error when writing to Google Sheets.

5. **Generate JSON Key**
   - Navigate to the **Keys** section of the service account.
   - Click **Add Key** and create a JSON key.
   - This will download a key file to your computer.

6. **Set Up Environment Variables**
   - Create a `.env` file in this directory (if it doesn’t already exist).
   - Add the following line to the `.env` file:
     ```plaintext
     SERVICE_ACCOUNT_CREDENTIALS=<contents-of-downloaded-keyfile>
     ```
   - Example:
    ```plaintext
    SERVICE_ACCOUNT_CREDENTIALS={"type":"service_account","project_id":"your-project-id","private_key_id":"your-private-key-id","private_key":"-----BEGIN PRIVATE KEY-----\\nMIIEvAIBADANBgkq...\\n-----END PRIVATE KEY-----\\n","client_email":"your-service-account-email@your-project-id.iam.gserviceaccount.com","client_id":"your-client-id","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://oauth2.googleapis.com/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url":"https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email%40your-project-id.iam.gserviceaccount.com"}
    ```

### 3. Define a config file to define constraints

1. **Create a new config file**: Navigate into the folder `gradescopeCronJob/config/`, and create a new config file with the naming scheme `{class}_{semester, year}.json`. For example, the file could be named `cs10_fall2024.json`. 

2. **Define the necessary constraints**:
   - **COURSE_ID**: The course ID is the final component of the URL on the Gradescope course homepage: `https://www.gradescope.com/courses/[COURSE_ID]`

   - **SCOPES**: This should not be modified by the user. Use `"https://www.googleapis.com/auth/spreadsheets"` to allow write access.

   - **SPREADSHEET_ID**: The spreadsheet ID is the final component of the spreadsheet’s URL: `https://docs.google.com/spreadsheets/d/[SPREADSHEET_ID]/edit?gid=0#gid=0`

   - **NUMBER_OF_STUDENTS**: The number of students enrolled in the course.

   - **UNGRADED_LABS**: Some labs are not included in the final grade calculation. `UNGRADED_LABS` is a list of such labs. For example, if labs 5 and 6 are not included, set `UNGRADED_LABS` to `[5, 6]`.

   - **TOTAL_LAB_POINTS**: Used only for the final grade calculation; this is the total number of lab points in a semester.

   - **NUM_LECTURES**: Used only for the final lecture-quiz grade calculation.

   - **SPECIAL_CASE_LABS**: A list of 4-part labs (lab assignments with four dropboxes, instead of the typical one or two).

   - **NUM_LECTURE_DROPS**: The number of drops included in the lecture-quiz grade calculation.

---

# 4. Docker Container

#### Prerequisites

- Docker installed on your system.

## Build and Run the Docker Container



### Step 1: Build the Docker Image

In this directory, run the following command to build the Docker image:

```bash
docker build -t gradescope-cron-job --build-arg PORT=8080 .
```

This command will create a Docker image with the cron job configuration and necessary dependencies. This includes the `--build-arg PORT=8080` flag to specify the `$PORT` variable from the build arg flag.


### Step 2: Run the Docker Container

Once the image is built, start the container in detached mode:

```bash
docker run -d --name gradescope-cron-container --expose 8080 -e PORT=8080 gradescope-cron-job
```

This command will run the container in the background. This exposes the port 8080 and sets the environment variable `PORT=8080`, which is the port that the google cloud service runs on by default.


### Step 3: Monitor the Logs

To view the cron job output, check the container logs. Use the following command to follow the logs in real-time:

```bash
docker logs -f gradescope-cron-container
```

Replace `gradescope-cron-job` with the actual container ID if needed. This command will display live logs, allowing you to monitor the cron job's execution.

### Example Log Command with Container ID

Alternatively, if you know the container ID, you can run:

```bash
docker logs -f e9b989ea03676f2141b1014891f436c7b3061320a479d8fa3231a4426c84d4c1
```
- e9b989ea03676f2141b1014891f436c7b3061320a479d8fa3231a4426c84d4c1 is an example to replace with the containerID.


## Configuration

- The cron job schedule and script configurations are set up within the Dockerfile and accompanying cron job files.
- Logs are stored in `/var/log/cron.log` within the container and are accessible through Docker logs as shown.

## Stopping the Container

To stop the running container:

```bash
docker stop gradescope-cron-container
```

## Removing the Container

If you wish to remove the container after stopping it:

```bash
docker rm gradescope-cron-container
```


## Troubleshooting

- **Container isn't starting**: Check Docker build output for errors during the image creation step.


## Deployment
- In the Google Cloud Artifact Registry, create a artifact registry repository


### **Step 1: Build the Docker Container**
Build the Docker container from the `Dockerfile`:
```bash
docker build -t gradescope-cron-job .
```

### **Step 2: Check if the Docker Image Exists**
Verify that the image was built successfully:
```bash
docker image ls
```

### **Step 3: Run the Docker Container on Port 8080**
Run the container and map it to port 8080 (matching the cloud deployment setup):
```bash
docker run -p 8080:8080 -e PORT=8080 gradescope-cron-job
```
- `-p 8080:8080`: Maps the host's port 8080 to the container's port 8080
- `-e PORT=8080`: Ensures the container is aware of the port configuration

### **Step 4: Tag the Docker Container**
Tag the Docker container with the destination in Google Cloud Artifact Registry:
```bash
docker tag gradescope-cron-job us-west2-docker.pkg.dev/eecs-gradeview/gradescopecronjob/gradescope-cron-job
```

### **Step 5: Initialize Google Cloud and Authorize**
Set up Google Cloud CLI and authenticate:
```bash
gcloud init
gcloud auth login
gcloud auth configure-docker us-west2-docker.pkg.dev
```

### **Step 6: Push the Tagged Docker Container**
Push the Docker image to Google Cloud Artifact Registry:
```bash
docker push us-west2-docker.pkg.dev/eecs-gradeview/gradescopecronjob/gradescope-cron-job
```


## Configuring secrets

1. Create the secrets and add permissions

```bash 
# Create secrets
gcloud secrets create GRADESCOPE_EMAIL --data-file=email.txt
gcloud secrets create GRADESCOPE_PASSWORD --data-file=password.txt
gcloud secrets create SERVICE_ACCOUNT --data-file=service-account.json

# Add permissions for your Cloud Run service account
gcloud secrets add-iam-policy-binding GRADESCOPE_EMAIL \
    --member="serviceAccount:<cloud-run-service-account>" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding GRADESCOPE_PASSWORD \
    --member="serviceAccount:<cloud-run-service-account>" \
    --role="roles/secretmanager.secretAccessor"

gcloud secrets add-iam-policy-binding SERVICE_ACCOUNT \
    --member="serviceAccount:<cloud-run-service-account>" \
    --role="roles/secretmanager.secretAccessor"
```

2. Verify the Secret
```bash
# List all secrets
gcloud secrets list

# Inspect the secret metadata
gcloud secrets describe SERVICE_ACCOUNT_CREDENTIALS

# Test access to the secret (displays the JSON content)
gcloud secrets versions access latest --secret="SERVICE_ACCOUNT_CREDENTIALS"
```

3. Fetch and use the secret in the application
```bash
gcloud secrets versions access latest --secret="SERVICE_ACCOUNT_CREDENTIALS" > /secrets/service-account.json
```
