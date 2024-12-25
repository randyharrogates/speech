





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