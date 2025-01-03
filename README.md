# Speech Project

This project consists of a full-stack application with a ReactJS frontend, a FastAPI backend, and SQLite as the database. It also uses OpenAI Whisper for transcription. Read architecture.pdf for a description of the design of the project.

* Note
Frontend for master branch is in a multi-page UI for better views. If needed, for single page UI, please use branch "v2_single_page"


## Application Architecture

<img width="783" alt="image" src="https://github.com/user-attachments/assets/a2d1a5b5-fe74-444f-8dac-a506d34ced79" />

## Requirements:

- Python: 3.9 - 3.12 (Please use python version 3.12 for best compatibility
- pip: latest version

### Installing FFmpeg for Local Development

- If you're running the application locally (not using Docker), you will need to install FFmpeg manually if your system does not have it installed, for the transcription functionality to work. Run the following command on terminal

- For macOS:

```bash
brew install ffmpeg
```

- For Linux:

```bash
sudo apt update
sudo apt install ffmpeg
```

## Starting the Backend

The backend is built using **FastAPI**. Follow these steps to start the backend:

### 1. Create a virtual environment**:
   
```bash
cd backend
python3 -m venv venv
```

### 2. Activate venv

On MacOS/Linux:

```bash
source venv/bin/activate
```

On windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Make sure you in the root folder and run the following command:

```bash
pip install --upgrade pip
pip install --upgrade setuptools
pip install -r requirements.txt
```

### 2. Run the command
```bash
cd ..
uvicorn backend.app.fastapi.main:app
```

## Starting the Frontend

The frontend is built using **ReactJS**. Follow these steps to start the frontend:

### 1. Install dependencies

Ensure that you are in the project root directory

```bash
cd frontend
npm install
```

### 2. Run the command
```bash
npm start
```

## Running Tests with `pytest`

Follow these steps to run the `pytest` tests in this project:

### 1. Install Dependencies

Make sure you have a virtual environment set up and activate it IF YOU HAVE NOT DONE SO. Run the following command in speech/backend:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt
```

### 2. Run test script

```bash
cd ..
pytest backend/tests/backend_test.py
```

## Running test for frontend

### 1. Install dependencies (If not already done so)

Ensure you are in the frontend folder "speech/frontend" and run the following command

```bash
npm install
```

### 2. Run test script

Ensure you are in the frontend folder "speech/frontend" and run the following command

```bash
npm test -- --watchAll --verbose
```

## How to build and run docker container for the application

Ensure you are in the root directory and run the following command:

```bash
docker-compose up --build
```


