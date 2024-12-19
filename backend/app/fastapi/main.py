# main.py
from fastapi import FastAPI, UploadFile, File, Request, APIRouter, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import requests
from pydantic import BaseModel
from dating_plan_ai_agents.objects.pinecone_manager import PineconeManager
from dating_plan_ai_agents.mongodb.mongo import MongoDBHelper
from dating_plan_ai_agents.fastapi import fastapi_helper
import json
from dotenv import load_dotenv
import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dating_plan_ai_agents.mongodb.user import User
from dating_plan_ai_agents.mongodb.schedule import Schedule
from fastapi.security import OAuth2PasswordRequestForm
from jwt import ExpiredSignatureError, InvalidTokenError
from jose.exceptions import JWSError
from botocore.exceptions import NoCredentialsError, ClientError

load_dotenv()
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from dating_plan_ai_agents.objects.utils import get_secret

# # Secret key for encoding and decoding JWT
is_test = True
if not is_test:
    try:
        secret = get_secret("my-app/config")
        SECRET_KEY = secret["JWT_SECRET_KEY"]
        ALGORITHM = secret["JWT_ALGO"]
        MONGO_URI = secret["MONGO_URI"]
        API_KEY = secret["API_KEY"]
        ORIGINS = secret["ALLOWED_ORIGINS"].split(",")
        PINECONE_KEY = secret["PINECONE_KEY"]
        GITHUB_TOKEN = secret["GITHUB_KEY"]
        print("Got secret from AWS secrets: {} {}".format(SECRET_KEY, ALGORITHM))
        print(
            f"Gettting secret from AWS: {MONGO_URI}, {API_KEY}, {ORIGINS}, {PINECONE_KEY}, {GITHUB_TOKEN}"
        )
    except (NoCredentialsError, ValueError, KeyError, ClientError, JWSError) as exp:
        print(f"Failed to get secret: {exp}, using default values")
        SECRET_KEY = os.getenv("JWT_SECRET_KEY")
        ALGORITHM = os.getenv("JWT_ALGO")
        MONGO_URI = os.getenv("MONGO_URI")
        API_KEY = os.getenv("API_KEY")
        ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
        PINECONE_KEY = os.getenv("PINECONE_KEY")
        GITHUB_TOKEN = os.getenv("GITHUB_KEY")
        print(
            f"Getting secreats from env: {SECRET_KEY}, {ALGORITHM}, {MONGO_URI}, {API_KEY}, {ORIGINS}, {PINECONE_KEY}, {GITHUB_TOKEN}"
        )

else:
    SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    ALGORITHM = os.getenv("JWT_ALGO")
    MONGO_URI = os.getenv("MONGO_URI")
    API_KEY = os.getenv("API_KEY")
    ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
    PINECONE_KEY = os.getenv("PINECONE_KEY")
    GITHUB_TOKEN = os.getenv("GITHUB_KEY")
    print(
        f"Getting secreats from env: {SECRET_KEY}, {ALGORITHM}, {MONGO_URI}, {API_KEY}, {ORIGINS}, {PINECONE_KEY}, {GITHUB_TOKEN}"
    )

ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()
router = APIRouter()
app.include_router(router)


class LogRequestMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Log the raw request body
        raw_body = await request.body()
        print(f"Raw incoming request: {raw_body}")

        try:
            # Parse the raw body into a dictionary
            body = json.loads(raw_body)
            print("Parsed request data with types:")
            for key, value in body.items():
                print(f"{key}: {value} (type: {type(value).__name__})")
        except json.JSONDecodeError:
            print("Failed to parse JSON body. Ensure the request contains valid JSON.")

        # Proceed with the normal request flow
        response = await call_next(request)
        return response


# Add the middleware to the app
app.add_middleware(LogRequestMiddleware)

# Add the CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,  # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI app"}


class DatePlanRequest(BaseModel):
    start_time: Optional[str] = None  # Start time
    end_time: Optional[str] = None  # End time
    indoor_outdoor: Optional[str] = None  # Indoor or outdoor preference
    country: Optional[str] = None  # Country
    budget: Optional[str] = None  # User's budget
    food_preference: Optional[str] = None  # Food preferences (e.g., vegetarian, etc.)
    activity_preference: Optional[str] = (
        None  # Activity preference (e.g., relaxing, adventurous)  ##
    )
    other_requirements: Optional[str] = None


# Get the current user's role from the token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # Extract user information
        user_id = payload.get("sub")  # Assuming "sub" contains the user ID
        user_role = payload.get("role")  # Assuming "role" contains the user's role

        # Ensure both user ID and role are present
        if not user_id or not user_role:
            raise credentials_exception

        return {"user_id": user_id, "role": user_role}

    except JWTError:
        raise credentials_exception  # Handles any JWT errors (invalid, expired, etc.)


# Check if the current user has admin privileges
async def is_admin(current_user: dict = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")


@app.post("/plan")
async def create_plan(
    request: DatePlanRequest,
    user: dict = Depends(get_current_user),
):
    # Here you would process the multi-agent loop
    # Extract user info
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID missing in token")

    start_time = request.start_time
    end_time = request.end_time
    indoor_outdoor = request.indoor_outdoor
    country = request.country
    budget = request.budget
    food_preference = request.food_preference
    activity_preference = request.activity_preference
    other_requirements = request.other_requirements

    result, final_state = fastapi_helper.create_workflow(
        {
            "start_time": start_time,
            "end_time": end_time,
            "indoor_outdoor": indoor_outdoor,
            "country": country,
            "budget": budget,
            "food_preference": food_preference,
            "activity_preference": activity_preference,
            "other_requirements": other_requirements,
        }
    )
    print(f"Final state type: {type(final_state)}, Final state: {final_state}")
    try:
        result = json.loads(result.strip())
        print(f"Json object:{type(result)}:\n {result}")
    except json.JSONDecodeError:
        result = {"error": "Invalid JSON response"}
    final_state["user_id"] = user_id
    final_state["activities"] = result["activities"]
    final_state["created_at"] = datetime.now()
    date_plan = Schedule.model_validate(final_state)
    schedule_manager = fastapi_helper.get_schedule_manager(mongo_uri=MONGO_URI)
    schedule_manager.insert_one(date_plan.model_dump())
    return {"result": result}  # Return the result as formatted JSON


@app.post("/ingest_mongodb_embeddings")
async def ingest_mongodb_embeddings():
    """
    Endpoint to retrieve documents from MongoDB, generate embeddings,
    and store them in Pinecone.
    """
    load_dotenv()
    openai_key = API_KEY
    pc_key = PINECONE_KEY
    pinecone_manager = PineconeManager(
        pc_api_key=pc_key,
        openai_key=openai_key,
        index_name="dating",
        mongodb_uri=MONGO_URI,
        mongodb_db="dating",
        mongodb_collection="reviews",
    )
    try:
        print("Ingesting MongoDB data into Pinecone...")
        # Trigger the ingestion of MongoDB data into Pinecone
        _ = pinecone_manager.ingest_mongodb(id_field="index_id", text_field="caption")
        return {"result": "Data successfully ingested into Pinecone"}
    except Exception as e:
        return {"error": str(e)}


@app.post("/upload-csv/")
async def upload_csv(file: UploadFile = File(...)):

    mongo_helper = MongoDBHelper(
        id_field="index_id",
        db_name="dating",
        collection_name="reviews",
        mongo_uri=MONGO_URI,
    )
    # Read the content of the uploaded file and convert it to MongoDB
    contents = await file.read()
    file_name = file.filename
    response = mongo_helper.convert_csv_to_mongodb(contents, file_name)

    return response


@app.get("/get_users", response_model=List[User])
async def get_users():
    users_collection, _ = fastapi_helper.get_user_manager(mongo_uri=MONGO_URI)
    users = []
    async for user in users_collection.find():
        users.append(user)

    for user in users:
        user["index_id"] = str(user["index_id"])  # Convert ObjectId to string
    return users


@app.get("/get_schedules", response_model=List[Schedule])
async def get_schedules():
    schedule_helper = MongoDBHelper(
        id_field="index_id",
        db_name="dating",
        collection_name="schedules",
        mongo_uri=MONGO_URI,
    )
    schedules = []
    async for schedule in schedule_helper.collection.find():
        schedules.append(schedule)
    return schedules


# JWT Utility functions
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        decoded_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_data
    except ExpiredSignatureError:
        print("The token has expired.")
        return None
    except InvalidTokenError:
        print("Invalid token.")
        return None


@app.post("/register")
async def create_user(
    user: User,
    is_admin: bool = Query(..., description="Indicates if the user is an admin"),
):
    # Log raw data for debugging (remove in production)
    for key, value in user.model_dump().items():
        print(f"{key}: {type(value).__name__}")
    users_collection, pwd_context = fastapi_helper.get_user_manager(mongo_uri=MONGO_URI)
    # Check if the email already exists
    existing_user = await users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Ensure users can only assign themselves as 'user', not 'admin'
    if user.role == "admin" and not is_admin:
        raise HTTPException(
            status_code=403, detail="Admin accounts can only be created by an admin"
        )

    # Hash the password before storing it
    hashed_password = pwd_context.hash(user.password)

    # Generate a new index_id (simple auto-generated index)
    total_users = await users_collection.count_documents({})
    new_index_id = total_users + 1
    print(f"New index id: {new_index_id}")

    # Create user document for MongoDB
    new_user = {
        "index_id": new_index_id,
        "name": user.name,
        "email": user.email,
        "password": hashed_password,
        "age": user.age,
        "role": user.role,  # Force all new users to have the 'user' role
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
    }

    # Insert the new user into the MongoDB collection
    await users_collection.insert_one(new_user)

    return {"message": "User created successfully"}


# Helper function to create JWT tokens


# Login endpoint
@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection, pwd_context = fastapi_helper.get_user_manager(mongo_uri=MONGO_URI)
    # Find user by email
    user = await users_collection.find_one({"email": form_data.username})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password
    if not fastapi_helper.verify_password(
        pwd_context=pwd_context,
        plain_password=form_data.password,
        hashed_password=user["password"],
    ):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=access_token_expires,
    )
    print(f"Logged in user: {user['email']}, Role: {user['role']}")
    print(f"Access token: {access_token}")
    return {"token": access_token}


class UserRoleResponse(BaseModel):
    role: str


@app.get("/get_user_role", response_model=UserRoleResponse)
async def get_user_role(token: str = Depends(oauth2_scheme)):
    # Use the token to get the user role
    try:
        email, role = fastapi_helper.get_user_role_from_token(
            token, SECRET_KEY, ALGORITHM
        )
        print(
            f"User's role in get_user's role: {role}, email: {email}"
        )  # Print the user's role ("role)
        if role is None:
            raise HTTPException(status_code=401, detail="Role not found in token")
        return {"role": role}  # Return the role
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")


# Endpoint to fetch schedules for a specific user
@app.get("/schedules")
async def get_user_schedules(user_id: str = Depends(get_current_user)):
    print(f'User_id is: {user_id["user_id"]}')
    user_id = user_id["user_id"]
    schedule_manager = fastapi_helper.get_schedule_manager(mongo_uri=MONGO_URI)
    user_schedules_cursor = schedule_manager.find({"user_id": user_id})
    user_schedules = await user_schedules_cursor.to_list(length=100)
    print(user_schedules)
    if not user_schedules:
        raise HTTPException(
            status_code=404,
            detail="No schedules found for the current user.\n Create more schedules now!",
        )
    print(f"User schedules found: {user_schedules}")
    return fastapi_helper.convert_objectid(user_schedules)


@app.get("/issues/")
async def get_github_issues(owner: str, repo: str):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        try:
            issues = response.json()  # Parse the JSON response
            return issues
        except requests.exceptions.JSONDecodeError as e:
            return {"error": "Invalid JSON response from GitHub API", "details": str(e)}
    else:
        return {
            "error": f"Failed to fetch issues from GitHub API. Status code: {response.status_code}",
            "content": response.text,
        }
