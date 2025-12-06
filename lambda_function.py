import json
import uuid
import boto3
from datetime import datetime

# Initialize DynamoDB resource outside the handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ai-microservice-results')

# Initialize Bedrock client
bedrock = boto3.client('bedrock-runtime')

def run_ai(text):
    # Calls Amazon Titan Text Lite to generate a summary of the input text
    response = bedrock.invoke_model(
        modelId='amazon.titan-text-lite-v1',
        accept='application/json',
        contentType='application/json',
        body=json.dumps({
            'inputText': text,
            'textGenerationConfig': {
                'maxTokenCount': 200,
                'temperature': 0.3
            }
        })
    )
    result = json.loads(response['body'].read())
    return result['results'][0]['outputText']

def lambda_handler(event, context):
    # Handle preflight OPTIONS request for CORS
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': ''
        }

    try:
        # Handle POST
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event

        text = body.get('text')
        if not text:
            return {
                'statusCode': 400,
                'headers': {'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Missing text'})
            }

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # AI summary using Bedrock
        ai_output = run_ai(text)

        ai_result = {
            'summary': ai_output,
            'length': len(text),
            'timestamp': datetime.now().isoformat()
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
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': json.dumps({
                'requestId': request_id,
                'result': ai_result
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST,OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '86400'
            },
            'body': json.dumps({'error': str(e)})
        }
