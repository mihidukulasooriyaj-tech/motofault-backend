from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime

app = FastAPI()

# MongoDB Atlas Cloud Connection
MONGO_URI = "mongodb+srv://mihidukulasooriyaj_db_user:THARU320@cluster0.d3ewlzj.mongodb.net/mt_one_db?retryWrites=true&w=majority"

client = AsyncIOMotorClient(MONGO_URI)
db = client.mt_one_db

# A separate collection is used to store motor fault records.
# This makes it easier to view and train different fault types separately.
collection = db.motor_fault_records


# Schema for receiving different sensor parameters and fault conditions
class MotorFaultInput(BaseModel):
    motorId: str
    faultType: str
    # Example: "Bearing Fault", "Stator Winding Unbalance", or "Normal"

    sensorParameters: Dict[str, Any]
    # A dictionary that can contain different sensor parameters
    # such as Current, RPM, Temperature, Vibration, etc.

    confidenceScore: float = 0.0
    # Confidence score provided by the ML model (optional)


@app.get("/")
def home():
    return {
        "message": "Motofault Multi-Parameter & Fault Detection Backend is Live!"
    }


# API endpoint to receive sensor data and fault information
# from the ESP32 or other devices using a POST request.
@app.post("/api/store-motor-fault")
async def store_motor_fault(data: MotorFaultInput):
    try:
        record = {
            "motorId": data.motorId,
            "faultType": data.faultType,
            "sensorParameters": data.sensorParameters,
            "confidenceScore": data.confidenceScore,
            "timestamp": datetime.now()
        }

        # Store the motor fault data in MongoDB Atlas
        await collection.insert_one(record)

        return {
            "success": True,
            "message": f"Fault record for {data.faultType} stored successfully in MongoDB!"
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
