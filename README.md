# Object Detection using OpenAI models

## Description

This project leverages the power of Azure OpenAI models to perform object detection on videos and images. The models we are leveraging from Azure OpenAI are: 1) gpt-4-vision-preview model and 2) gpt-4o model. The application consists of two main components: a FastAPI backend for processing videos, images and a Streamlit frontend for uploading videos, images and displays detection results as desciption of the keyframes and images along with JSON.

- Azure OpenAI documentation, visit: [Azure OpenAI documentation](https://learn.microsoft.com/en-us/azure/ai-services/openai/)
- Azure OpenAI portal link, visit: [Azure OpenAI portal](https://portal.azure.com/#view/Microsoft_Azure_ProjectOxford/CognitiveServicesHub/~/OpenAI)
- For pricing of the Azure OpenAI models, visit: [Pricing for the Azure OpenAI models](https://azure.microsoft.com/en-in/pricing/details/cognitive-services/openai-service/)
- For pricing calculator, visit: [Microsoft pricing calculator](https://azure.microsoft.com/en-in/pricing/calculator/?ef_id=_k_EAIaIQobChMI5ObLysfQhwMVOyZ7Bx3g2jwQEAAYASAAEgIiI_D_BwE_k_&OCID=AIDcmmf1elj9v5_SEM__k_EAIaIQobChMI5ObLysfQhwMVOyZ7Bx3g2jwQEAAYASAAEgIiI_D_BwE_k_&gad_source=1&gbraid=0AAAAADcJh_siESvMQ_A3T7JFlPexHp1I9&gclid=EAIaIQobChMI5ObLysfQhwMVOyZ7Bx3g2jwQEAAYASAAEgIiI_D_BwE)
- Scenedetect library documentation, visit: [Scenedetect](https://www.scenedetect.com/docs/latest/)

## Features

- Object Detection: Detect objects in videos and images utilising the Azure OpenAI models like gpt-4-vision-preview model and gpt-4o model.
- FastAPI: Backend service for handling video and image processing requests.
- Streamlit: Frontend interface for uploading videos and images which displays detection results as desciption of the keyframes and images along with JSON.
- Docker: Containerized application setup for easy deployment.

### Installation

#### Prerequisites

- Docker
- Colima

## Steps

3. ***Create requirements.txt:***
   ```sh
   pip install pipreqs
   pipreqs
   ```

Open requirements.txt and ensure it includes the following:

- fastapi==0.115.4
- numpy==2.1.3
- openai==0.28.0
- opencv_python==4.10.0.84
- opencv_python_headless==4.10.0.84
- pydantic==2.9.2
- Requests==2.32.3
- scenedetect==0.6.4
- streamlit==1.39.0
- uvicorn
- python-multipart

4. Install all dependencies:

   ```sh
   poetry install

   ```

5. Activate the virtual environment:
   ```sh
   poetry shell
   ```

Now we run our applications or we can use docker with poetry as well.

6. **Start Colima:**

   ```sh
   colima start

   ```

7. Navigate to the project directory:
   ```sh
   cd <repository-directory>
   ```

## Configuration

### 1. Config.py file

```
import openai

# Set up Azure OpenAI credentials
class OpenAIConfig:
    api_type = "azure"
    api_base = "Write your api_base or endpoint here."
    api_version = "2023-06-01-preview"
    api_key = "Write your api_key here."

    @classmethod
    def configure_openai(cls):
        openai.api_type = cls.api_type
        openai.api_base = cls.api_base
        openai.api_version = cls.api_version
        openai.api_key = cls.api_key

# Call this at the start of your app to configure OpenAI
OpenAIConfig.configure_openai()
```

Update the api_base and api_key fields with the correct Azure OpenAI endpoint and API key to enable model access.

### 2. Dockerfile

```dockerfile
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

# Copy pyproject.toml and poetry.lock (if available) to the container
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install poetry

# Install project dependencies using Poetry (without dev dependencies)
RUN poetry install --no-dev

# Install additional dependencies explicitly
RUN poetry add uvicorn torch torchvision opencv-python-headless

# Copy the rest of the application code into the container
COPY . /app/

# Expose port 8000 for FastAPI
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["poetry", "run", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]


```

### 3. Dockerfile

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Install required system libraries for OpenCV and other dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    && apt-get clean

# Set the working directory in the container
WORKDIR /app

# Copy pyproject.toml and poetry.lock to the container
COPY pyproject.toml poetry.lock* /app/

# Install Poetry
RUN pip install poetry

# Install project dependencies using Poetry (without dev dependencies)
RUN poetry install --no-dev

# Copy the rest of the application code into the container
COPY . /app/

# Expose port 8501 for Streamlit
EXPOSE 8501

# Command to run the Streamlit app
CMD ["poetry", "run", "streamlit", "run", "app.py"]

```

### 4. docker-compose.yml

```yaml
services:
  fastapi_container:
    build:
      context: .
      dockerfile: Dockerfile # Corrected dockerfile path
    container_name: fastapi_container
    ports:
      - "8000:8000"
    networks:
      - mynetwork

  streamlit_container:
    build:
      context: ./frontend # Corrected context for frontend directory
      dockerfile: Dockerfile # Corrected dockerfile name
    container_name: streamlit_container
    ports:
      - "8501:8501"
    depends_on:
      - fastapi_container
    networks:
      - mynetwork

networks:
  mynetwork:
    driver: bridge
```

## Usage

### 1. Build and start the Docker containers:

```ssh
docker-compose up --build
```

### 2. After the initial build, to rerun the Docker containers without rebuilding, use:

```ssh
docker-compose up
```

### 3. Access the applications:

- FastAPI: http://localhost:8000/docs
- Streamlit: http://localhost:8501

### 4. Upload a video through the Streamlit interface to test object detection.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any features, bug fixes, or suggestions.

## Acknowledgements

- The developers of Azure OpenAI for their powerful models.
- The FastAPI and Streamlit communities for their excellent frameworks.
