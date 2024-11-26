# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /gradescopeCronJob
WORKDIR /gradescopeCronJob

ENV PORT=$PORT

# Install necessary packages
RUN apt-get update && \
    apt-get install -y cron bash

COPY . /gradescopeCronJob

RUN pip install --no-cache-dir -r requirements.txt

# Allow the cron to execute the script as an executable
RUN chmod u+x gradescope_to_spreadsheet.py

# Copy the local cron job file to the container's cron.d directory
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
RUN chmod u+w /etc/cron.d/cronjob

# Start the cron daemon
RUN cron start

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Expose the hc server port
EXPOSE 8080

# Run the hc server
CMD python server.py

