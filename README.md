AI Text Summarizer Microservice

This project is a serverless text processing microservice built with AWS Lambda, API Gateway, DynamoDB, and Amazon Bedrock. It allows users to submit text via a static website and receive a polite acknowledgment response while logging the input and AI-generated summaries for internal tracking.

Features:
- Serverless architecture: AWS Lambda handles all requests.
- API Gateway integration: Exposes a /process endpoint for POST requests.
- DynamoDB logging: Stores each request with a unique ID, timestamp, original text, and AI-generated summary.
- Bedrock integration: Uses Amazon Titan LLM for text summarization (fallback placeholder logic if Bedrock is unavailable).
- CORS support: Static website can call the Lambda from any origin.
- Plain-text user responses: Returns a polite acknowledgment instead of raw AI output.
- Fallback messaging: Ensures the user always receives a consistent, friendly message even if AI or Bedrock fails.

Architecture:

[Static Website] --> [API Gateway /process] --> [Lambda Function] --> [DynamoDB]
                                         \
                                          -> [Amazon Bedrock (optional AI summary)]

- Users submit text via the static website.
- Lambda receives the POST request, generates a request ID, invokes Bedrock (or fallback logic), and logs results in DynamoDB.
- Lambda responds to the user with a plain-text acknowledgment message.

Getting Started

Prerequisites:
- AWS account with access to Lambda, API Gateway, DynamoDB, and optionally Bedrock.
- S3 bucket to host the static website.
- Python 3.9+ for Lambda runtime.

Deployment:

1. Create DynamoDB table:
   Table name: ai-microservice-results
   Primary key: requestID (String)

2. Deploy Lambda function:
   - Runtime: Python 3.9+
   - Attach a role with:
     - DynamoDB FullAccess (or fine-grained PutItem permissions)
     - LambdaBasicExecutionRole
     - Bedrock access if using AI

3. Create API Gateway endpoint:
   - Resource: /process
   - Method: POST
   - Integration: Lambda function
   - Enable CORS

4. Update static website:
   - Set apiUrl in script to your API Gateway invoke URL:
     const apiUrl = "https://<api-id>.execute-api.<region>.amazonaws.com/<stage>/process";
   - Upload HTML/CSS/JS files to S3 (or serve via any static hosting).

Usage:

1. Open the static website in a browser.
2. Enter your text in the textarea and click Submit.
3. The website displays a plain-text acknowledgment:
   Request <request_id>: Thank you for your inquiry! We have received your request and will get back to you.
4. All requests are logged in DynamoDB with AI-generated summaries (for internal reference).

Example:

Input text:
Hello, my internet is down and I cannot access my email.

Response displayed to user:
Request 123e4567-e89b-12d3-a456-426614174000: Thank you for your inquiry! We have received your request and will get back to you.

DynamoDB entry:
{
  "requestID": "123e4567-e89b-12d3-a456-426614174000",
  "inputText": "Hello, my internet is down and I cannot access my email.",
  "result": {
    "summary": "Bedrock-generated summary or fallback message",
    "length": 67,
    "timestamp": "2025-12-07T18:14:47.495647"
  }
}

Notes:
- The user-facing message is intentionally generic for consistent UX.
- Bedrock is optional; the Lambda can run purely with fallback logic.
- Plain-text responses avoid JSON parsing errors in the static site frontend.
- CORS headers allow the static site to call Lambda from any origin.

Author:
Kai Peters
GitHub Profile: https://github.com/kaipeters1994
