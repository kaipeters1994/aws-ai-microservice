import json
import uuid
import boto3
from datetime import datetime
import re

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
    "Content-Type": "text/plain",  # plain text for end user
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "POST,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400"
}

# Smart fallback summarization
def simple_summary(text, max_sentences=2):
    sentences = re.split(r'(?<=[.!?]) +', text)
    return ' '.join(sentences[:max_sentences])

# Optional keyword-based responses for edge cases
def keyword_response(text):
    lower = text.lower()
    if 'internet' in lower:
        return "It looks like your internet is down. Check your modem lights, ensure cables are connected, and restart your router."
    if 'help' in lower:
        return "I can assist with information and summaries! Please provide a topic or question."
    return None

def run_ai(text):
    """
    Returns a summary of the input text.
    Uses Bedrock if available, otherwise falls back to smart placeholder logic.
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
            fb = keyword_response(text)
            if fb:
                return fb
            return simple_summary(text)

    # Fallback if Bedrock not enabled
    fb = keyword_response(text)
    if fb:
        return fb
    return simple_summary(text)

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

        # AI summary
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

        # Return plain text to end user
        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': f"Request {request_id}: {ai_output}"
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': f"Error: {str(e)}"
        }
