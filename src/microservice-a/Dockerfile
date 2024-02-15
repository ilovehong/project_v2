# Use an official Python runtime as a base image
FROM python:3.9-slim

# Set the working directory to /app in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application's source code into the container at /app
COPY . /app

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Dapr HTTP port (Optional, if you want to specify)
ENV DAPR_HTTP_PORT=3500

# Run app.py when the container launches
CMD ["python", "app_a.py"]
