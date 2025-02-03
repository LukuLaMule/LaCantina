# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Install poppler-utils for pdf2image
RUN apt-get update && apt-get install -y poppler-utils

# Make port 80 available to the world outside this container
EXPOSE 80

# Run LaCantina.py when the container launches
CMD ["python", "LaCantina.py"]

