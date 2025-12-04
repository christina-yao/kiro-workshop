import boto3
from botocore.exceptions import ClientError
import os
from typing import List, Optional
import uuid

class DynamoDBClient:
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = os.getenv('DYNAMODB_TABLE_NAME', 'events-table')
        self.table = self.dynamodb.Table(self.table_name)
    
    def create_event(self, event_data: dict) -> dict:
        event_id = str(uuid.uuid4())
        event_data['eventId'] = event_id
        
        try:
            self.table.put_item(Item=event_data)
            return event_data
        except ClientError as e:
            raise Exception(f"Error creating event: {e.response['Error']['Message']}")
    
    def get_event(self, event_id: str) -> Optional[dict]:
        try:
            response = self.table.get_item(Key={'eventId': event_id})
            return response.get('Item')
        except ClientError as e:
            raise Exception(f"Error getting event: {e.response['Error']['Message']}")
    
    def list_events(self) -> List[dict]:
        try:
            response = self.table.scan()
            return response.get('Items', [])
        except ClientError as e:
            raise Exception(f"Error listing events: {e.response['Error']['Message']}")
    
    def update_event(self, event_id: str, update_data: dict) -> dict:
        update_expr = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expr_attr_names = {f"#{k}": k for k in update_data.keys()}
        expr_attr_values = {f":{k}": v for k, v in update_data.items()}
        
        try:
            response = self.table.update_item(
                Key={'eventId': event_id},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_attr_names,
                ExpressionAttributeValues=expr_attr_values,
                ReturnValues="ALL_NEW"
            )
            return response.get('Attributes')
        except ClientError as e:
            raise Exception(f"Error updating event: {e.response['Error']['Message']}")
    
    def delete_event(self, event_id: str) -> bool:
        try:
            self.table.delete_item(Key={'eventId': event_id})
            return True
        except ClientError as e:
            raise Exception(f"Error deleting event: {e.response['Error']['Message']}")

db_client = DynamoDBClient()
