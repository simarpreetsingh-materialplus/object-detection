# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for tkinter, OpenCV, and necessary libraries
RUN apt-get update && apt-get install -y \
    python3-tk \
    libopencv-dev \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && apt-get clean

# Copy requirements.txt to the container
COPY requirements.txt /app/

# Install project dependencies using pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . /app/

# Set the PYTHONPATH environment variable
ENV PYTHONPATH="/app"

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
