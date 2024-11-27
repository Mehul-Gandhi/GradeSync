# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /gradescopeCronJob
WORKDIR /gradescopeCronJob

# The port is defined by the Cloud Run Service
# $PORT 
ENV PORT=$PORT

# Install necessary packages
RUN apt-get update && \
    apt-get install -y cron bash

# Copy the current directory contents into the container at /gradescopeCronJob
COPY . /gradescopeCronJob

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Allow the cron to execute the script as an executable
# chmod: Changes to the file permissions
# u: Refers to the "user" (the owner of the file).
# +x: Adds execute permission for the specified group (u here).
RUN chmod u+x gradescope_to_spreadsheet.py

# Copy the local cron job file to the container's cron.d directory
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
# u: Refers to the "user" (the owner of the file).
# +x: Adds execute permission for the specified group (u here).
RUN chmod u+w /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Expose the healthcheck server port
# The healthcheck is required by the Cloud Run Service
EXPOSE 8080

# Start the cron daemon &&
# Run the healthcheck server when the container launches
CMD service cron start && python server.py

