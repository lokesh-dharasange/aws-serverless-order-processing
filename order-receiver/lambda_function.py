import json
import boto3
import uuid
from datetime import datetime

sqs = boto3.client("sqs")
QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/805370850931/OrderProcessingQueue"

def lambda_handler(event, context):
    try:
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        
        # Create order
        order = {
            "orderId": str(uuid.uuid4()),
            "customerName": body.get("customerName", "Unknown"),
            "items": body.get("items", []),
            "totalAmount": body.get("totalAmount", 0),
            "status": "PENDING",
            "createdAt": datetime.utcnow().isoformat()
        }
        
        # Send to SQS
        sqs.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(order),
            MessageAttributes={
                "OrderType": {
                    "DataType": "String",
                    "StringValue": body.get("orderType", "STANDARD")
                }
            }
        )
        
        return {
            "statusCode": 202,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Order received",
                "orderId": order["orderId"]
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
