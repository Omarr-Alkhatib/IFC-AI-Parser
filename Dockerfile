# Use a lightweight official Python runtime as the base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy dependency specifications first to leverage Docker layer caching
COPY requirements.txt .

# Install the required Python packages without caching logs to keep image size small
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application source code into the container
COPY app.py .

# Define the default executable command when the container runs
ENTRYPOINT ["python", "app.py"]