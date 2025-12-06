AWS AI Microservice Project

Project Overview:
This project is a simple serverless AI microservice I built using AWS Lambda, API Gateway, DynamoDB, and GitHub Actions. The main idea is that you can send text to the API, it does some basic processing (like summarizing the text), stores the results in DynamoDB, and gives back the output.

I also set up GitHub Actions with OIDC authentication, so the Lambda function deploys automatically without using long-term AWS keys.

Architecture:
GitHub Actions → Lambda (aiProcessor) → DynamoDB
API Gateway → Lambda

How it works:
	1.	Push code to GitHub, triggers GitHub Actions workflow
	2.	GitHub assumes AWS role via OIDC
	3.	Lambda function is deployed automatically
	4.	API Gateway receives HTTP requests - triggers Lambda
	5.	Lambda processes input - saves result to DynamoDB - returns response

Features:
	•	API Gateway HTTP endpoint for sending text
	•	Lambda function with basic AI logic: summarizes text (first 150 characters), shows length of text and timestamp
	•	Stores results in DynamoDB with unique request IDs
	•	GitHub Actions workflow automatically deploys Lambda on push

Getting Started:
Prerequisites:
	•	AWS Account
	•	GitHub Account
	•	Python 3 
	•	Postman or another HTTP client

Setup:
	1.	Clone the repo
	2.	Install dependencies (if any Python packages are used)
	3.	GitHub Actions will deploy Lambda automatically on push to main.

Using the API:
Endpoint: https://<API_GATEWAY_ID>.execute-api..amazonaws.com/process
Method: POST
Body example:
{ “text”: “Your text here” }

Example Response:
{
“requestId”: “ed0cb8e4-4e85-402a-a5da-f39fcf6535da”,
“result”: {
“summary”: “Your text here”,
“length”: 28,
“timestamp”: “2025-12-05T21:51:30.823518”
}
}

Project Structure:
aws-ai-microservice/
	•	lambda_function.py        # Lambda code
	•	README.txt (or README.md)
	•	docs/screenshots/        # Screenshots for documentation
	•	tests/                   # Optional: unit tests
	•	.github/workflows/deploy.yml  # GitHub Actions workflow

GitHub Actions Workflow:
	•	Runs when code is pushed to main branch
	•	Steps:

	1.	Checkout code
	2.	Configure AWS credentials via OIDC
	3.	Package Lambda function
	4.	Deploy Lambda

Future Plans:
	•	Improve AI logic (like sentiment analysis or better summarization)
	•	Add unit tests and integrate them into workflow
	•	Add API authentication (Cognito or API keys)
	•	Deploy multiple Lambda functions in the workflow

Use Case of Project:
    1. Could be used for customer support text summarization.

Author:
Kai Peters
GitHub Profile: https://github.com/kaipeters1994
