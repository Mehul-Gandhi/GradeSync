# Base image with Python and cron
FROM python:3.11-slim

# Set up work directory
WORKDIR /gradescopeCronJob

# Copy all files
COPY . /gradescopeCronJob

RUN pip install --no-cache-dir -r requirements.txt

# Copy the Python script to the Docker container
COPY gradescope_to_spreadsheet.py .

# Install cron
RUN apt-get update && apt-get install -y cron bash

# Add the cron job
COPY crontab /etc/cron.d/grade_cron

# Grant execution rights to the cron job
RUN chmod 0644 /etc/cron.d/grade_cron

# Create a log file to be able to inspect cron job execution
RUN touch /var/log/cron.log

# Run the command on container startup
CMD python /gradescopeCronJob/gradescope_to_spreadsheet.py >> /var/log/cron.log 2>&1 && cron && tail -f /var/log/cron.log
#CMD cron && tail -f /var/log/cron.log
