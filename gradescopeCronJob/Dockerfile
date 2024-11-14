# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory to /gradescopeCronJob
WORKDIR /gradescopeCronJob
COPY . /gradescopeCronJob

RUN pip install --no-cache-dir -r requirements.txt

# Install necessary packages
RUN apt-get update && \
    apt-get install -y cron bash

# Copy the local cron job file to the container's cron.d directory
COPY cronjob /etc/cron.d/cronjob

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/cronjob

# Apply the cron job
RUN crontab /etc/cron.d/cronjob

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Start cron in the background
CMD ["sh", "-c", "cron -f & tail -f /var/log/cron.log"]
#CMD ["sh", "-c", "cron -f & tail -f /var/log/cron.log"]
