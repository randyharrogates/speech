from typing import Any
from dating_plan_ai_agents.objects.state import GraphState
from dating_plan_ai_agents.objects.budget_agent import BudgetAgent
from dating_plan_ai_agents.objects.evaluator import Evaluator
from dating_plan_ai_agents.objects.input_agent import InputValidator
from dating_plan_ai_agents.objects.location_agent import LocationAgent
from dating_plan_ai_agents.objects.schedule_agent import SchedulingAgent
from dating_plan_ai_agents.objects.final_agent import FinalPlan
from dating_plan_ai_agents.mongodb.mongo import MongoDBHelper
from langgraph.graph import StateGraph, END
from bson import ObjectId
from passlib.context import CryptContext
from jose import jwt


def create_workflow(inputs: dict[str, Any]):
    # Here you would process the multi-agent loop
    start_time = inputs.get("start_time", "No start time yet")
    end_time = inputs.get("end_time", "No end time yet")
    indoor_outdoor = inputs.get("indoor_outdoor", "No indoor/outdoor preference yet")
    country = inputs.get("country", "No country preference yet")
    budget = inputs.get("budget", "No budget yet")
    food_preference = inputs.get("food_preference", "No food preference yet")
    activity_preference = inputs.get(
        "activity_preference", "No activity preference yet"
    )
    other_requirements = inputs.get("other_requirements", "No other requirements yet")
    result = None
    # Process the inputs and create a plan
    dating_review_workflow = StateGraph(GraphState)

    _create_workflow(dating_review_workflow)
    state = GraphState(
        total_iterations=0,  # Initialize iteration counter
        budget=budget,  # Example user input
        start_time=start_time,
        end_time=end_time,
        country=country,
        food_preference=food_preference,
        indoor_outdoor=indoor_outdoor,
        activity_preference=activity_preference,
        other_requirements=other_requirements,
    )
    print("Workflow created...")
    # Execute the workflow
    result = dating_review_workflow.compile()
    conversation = result.invoke(
        state, {"recursion_limit": 100}, stream_mode="values", debug=True
    )
    final_schedule = (
        conversation.get("final_schedule").replace("```", "").replace("json", "")
    )
    conversation["final_schedule"] = final_schedule
    return final_schedule, conversation


def _create_workflow(dating_review_workflow: StateGraph):

    input_validator = InputValidator()
    location_selector = LocationAgent()
    scheduling_agent = SchedulingAgent()
    budget_reviewer = BudgetAgent()
    evaluator = Evaluator()
    finalize_plan = FinalPlan()
    dating_review_workflow.add_node("input_validator", input_validator.run)
    dating_review_workflow.add_node("location_selector", location_selector.run)
    dating_review_workflow.add_node("scheduling_agent", scheduling_agent.run)
    dating_review_workflow.add_node("budget_reviewer", budget_reviewer.run)
    dating_review_workflow.add_node("evaluator", evaluator.run)
    dating_review_workflow.add_node("finalize_plan", finalize_plan.run)

    # Set entry point
    dating_review_workflow.set_entry_point("input_validator")
    # Add edges for transitions, including evaluator
    dating_review_workflow.add_edge("input_validator", "scheduling_agent")
    dating_review_workflow.add_edge("scheduling_agent", "location_selector")
    dating_review_workflow.add_edge("location_selector", "budget_reviewer")

    dating_review_workflow.add_conditional_edges(
        "budget_reviewer",
        evaluator.run,
        {"scheduling_agent", "finalize_plan"},
    )
    # Add END condition for budget reviewer (final step before evaluation)
    dating_review_workflow.add_edge("finalize_plan", END)


def get_user_manager(mongo_uri: str):
    # MongoDB setup
    user_helper = MongoDBHelper(
        id_field="index_id",
        db_name="dating",
        collection_name="users",
        mongo_uri=mongo_uri,
    )
    users_collection = user_helper.collection

    # Password hashing function
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return users_collection, pwd_context


def verify_password(pwd_context, plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_user_role_from_token(token: str, secret_key: str, algorithm: str) -> str:

    # Decode the token using the SECRET_KEY and ALGORITHM
    payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    # You should have 'role' in the token's payload, for example {'sub': 'user@example.com', 'role': 'admin'}
    email = payload.get("sub")
    role = payload.get("role")
    print(f"User's role in get_user_role_form_token role: {role}")
    return email, role


def get_schedule_manager(mongo_uri: str):
    schedule_helper = MongoDBHelper(
        id_field="index_id",
        db_name="dating",
        collection_name="schedules",
        mongo_uri=mongo_uri,
    )
    schedule_collection = schedule_helper.collection
    return schedule_collection


def convert_objectid(obj):
    if isinstance(obj, ObjectId):
        return str(obj)  # Convert ObjectId to string
    if isinstance(obj, dict):
        return {key: convert_objectid(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [convert_objectid(item) for item in obj]
    return obj
