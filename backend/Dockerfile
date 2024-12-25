# Use a Python 3.12 base image
FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Install FFmpeg for audio processing
RUN apt-get update && \
    apt-get install -y ffmpeg

# Copy the requirements file into the container
COPY backend/requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install --upgrade setuptools && \
    pip install -r requirements.txt

# Copy the backend application code into the container
COPY . /app/

# Expose the FastAPI application on port 8000
EXPOSE 8000

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "backend.app.fastapi.main:app", "--host", "0.0.0.0", "--port", "8000"]
