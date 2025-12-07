import json
import uuid
import boto3
from datetime import datetime

# Initialize DynamoDB resource outside the handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ai-microservice-results')

# Try to initialize Bedrock client
try:
    bedrock = boto3.client('bedrock-runtime')
    BEDROCK_ENABLED = True
except Exception:
    bedrock = None
    BEDROCK_ENABLED = False

# Common CORS headers
CORS_HEADERS = {
    "Content-Type": "text/plain",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400"
}

def run_ai(text):
    """
    Returns a summary of the input text.
    Uses Bedrock if available, otherwise falls back to placeholder logic.
    """
    if BEDROCK_ENABLED:
        try:
            response = bedrock.invoke_model(
                modelId='amazon.titan-text-lite-v1',
                accept='application/json',
                contentType='application/json',
                body=json.dumps({
                    'inputText': text,
                    'textGenerationConfig': {
                        'maxTokenCount': 400,
                        'temperature': 0.7
                    }
                })
            )
            body_content = response['body'].read()
            result = json.loads(body_content)
            if 'results' in result and len(result['results']) > 0:
                return result['results'][0].get('outputText', 'No output returned from Bedrock')
            else:
                return 'No output returned from Bedrock'
        except Exception as e:
            print("Bedrock error:", str(e))
            return "Thank you for your inquiry! We have received your request and will get back to you."
    
    # Fallback message if Bedrock not available
    return "Thank you for your inquiry! We have received your request and will get back to you."

def lambda_handler(event, context):
    # Handle CORS preflight OPTIONS request
    if event.get("httpMethod") == "OPTIONS":
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': ''
        }

    try:
        # Parse POST request
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event

        text = body.get('text')
        if not text:
            return {
                'statusCode': 400,
                'headers': CORS_HEADERS,
                'body': 'Missing text'
            }

        # Generate unique request ID
        request_id = str(uuid.uuid4())

        # AI summary (for logging)
        ai_output = run_ai(text)

        ai_result = {
            'summary': ai_output,
            'length': len(text),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Save results to DynamoDB
        table.put_item(Item={
            'requestID': request_id,
            'inputText': text,
            'result': ai_result
        })

        # Return polite, generic message to the user
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': f"Request {request_id}: Thank you for your inquiry! We have received your request and will get back to you."
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': f"Error: {str(e)}"
        }
