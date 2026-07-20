import json
import uuid
import boto3
from decimal import Decimal
from datetime import datetime

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

TABLE_NAME = "OrdersNew"
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:805370850931:OrderNotifications"

def lambda_handler(event, context):

    table = dynamodb.Table(TABLE_NAME)

    for record in event["Records"]:

        body = json.loads(record["body"])

        order = {
            "orderId": body.get("orderId") or str(uuid.uuid4()),
            "createdAt": body.get("createdAt") or datetime.utcnow().isoformat(),
            "customerName": body.get("customerName", "Unknown"),
            "items": body.get("items", []),
            "totalAmount": Decimal(str(body.get("totalAmount", 0))),
            "status": "PROCESSED",
            "processedAt": datetime.utcnow().isoformat()
        }

        print("ORDER =", order)

        table.put_item(
            Item={
                "orderId": order["orderId"],
                "createdAt": order["createdAt"],
                "customerName": order["customerName"],
                "items": order["items"],
                "totalAmount": order["totalAmount"],
                "status": order["status"],
                "processedAt": order["processedAt"]
            }
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="New Order Processed",
            Message=json.dumps(order, default=str)
        )

    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Success"})
    }
