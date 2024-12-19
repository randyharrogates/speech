from motor.motor_asyncio import AsyncIOMotorClient
from dating_plan_ai_agents.mongodb.review import Review
import pandas as pd
import io
from dating_plan_ai_agents.objects.utils import get_secret
from jose.exceptions import JWSError
from botocore.exceptions import NoCredentialsError, ClientError

class MongoDBHelper:

    def __init__(
        self, id_field, db_name, collection_name, mongo_uri="mongodb://localhost:27017"
    ):
        self.mongo_uri = mongo_uri
        self.id_field = id_field
        self.db_name = db_name
        self.collection_name = collection_name
        print(f"Initializing MongoDBHelper with URI: {self.mongo_uri}")
        self.client = AsyncIOMotorClient(self.mongo_uri)
        print(f"MongoDB client initialized: {self.client}")
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        # Create index for 'index_id' if it doesn't exist (ensure uniqueness)
        self.collection.create_index(id_field, unique=True)

    async def convert_csv_to_mongodb(self, contents, filename=None):
        try:
            # Read CSV data into a DataFrame
            df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
            # Convert DataFrame to a list of dictionaries
            records = df.to_dict(orient="records")
            # Validate and transform data using the Review class
            validated_records = []
            for row in records:
                try:
                    # Validate each row with the Review class
                    review = Review(
                        index_id=row["index_id"],
                        caption=row["caption"],
                        name=row["name"],
                        overall_rating=row["overall_rating"],
                        category=row["category"],
                        opening_hours=row.get("opening_hours", None),
                    )
                    validated_records.append(
                        review.model_dump()
                    )  # Convert the validated model to a dictionary
                except (ValueError, TypeError, KeyError) as exp:
                    # Log validation errors and skip invalid rows
                    print(f"Validation error for row {row}: {exp}")

            # Use asynchronous `update_one` method
            for record in validated_records:
                await self.collection.update_one(
                    {"index_id": record["index_id"]},  # Search by unique identifier
                    {"$setOnInsert": record},  # Insert only if not already present
                    upsert=True,  # Create a new document if not found
                )
            return {
                "message": f"File '{filename}' uploaded and validated records inserted into MongoDB successfully."
            }
        except Exception as e:
            return {"Error in convert_to_mongodb_func": str(e)}
