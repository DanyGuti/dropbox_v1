# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app/tmp

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Install any necessary dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install inotify-tools (Linux-specific)
RUN apt-get update

# Run the application
CMD ["python", "client_watcher.py"]