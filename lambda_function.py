import json
import uuid
import boto3
from datetime import datetime

# Initialize DynamoDB resource outside the handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ai-microservice-results')


def lambda_handler(event, context):
    try:
        # Handle direct HTTP API JSON input
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event

        text = body.get('text')
        if not text:
            return {'statusCode': 400, 'body': json.dumps({'error': 'Missing text'})}

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # Placeholder AI logic
        ai_result = {
            'summary': text[:150] + ('...' if len(text) > 150 else ''),
            'length': len(text),
            'timestamp': datetime.utcnow().isoformat(),
        }

        # Save results to DynamoDB
        table.put_item(Item={
            'requestID': request_id,
            'inputText': text,
            'result': ai_result
        })

        # Return processed result
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'requestId': request_id,
                'result': ai_result
            })
        }

    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}