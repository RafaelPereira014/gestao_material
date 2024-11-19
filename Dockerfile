# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies from requirements.txt
RUN pip install  -r requirements.txt

# Expose the port the app will run on
EXPOSE 8081

# Define the command to run your Flask app
CMD ["python3", "run.py"]