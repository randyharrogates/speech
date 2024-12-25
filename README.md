# Speech Project

This project consists of a full-stack application with a ReactJS frontend, a FastAPI backend, and SQLite as the database. It also uses OpenAI Whisper for transcription.

## Starting the Backend

The backend is built using **FastAPI**. Follow these steps to start the backend:

### 1. Install Dependencies

Make sure you in the root folder and run the following command:

```bash
cd backend
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

Make sure you have a virtual environment set up and activate it IF YOU HAVE NOT DONE SO:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

pip install -r requirements.txt
```

### 2. Run test script
Ensure you are in the root project folder "speech" and run the following command

```bash
pytest backend/tests/backend_test.py
```


## Running test for frontend
### 1. Install dependencies

### 2. Run test script

Ensure you are in the frontend folder "speech/frontend" and run the following command

```bash
npm test -- --watchAll --verbose
```