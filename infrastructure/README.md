# CDK Infrastructure

Deploys the Events API using:
- AWS Lambda (FastAPI with Mangum)
- API Gateway (REST API)
- DynamoDB (events table)

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Deploy

Quick deploy:
```bash
./deploy.sh
```

Or manually:
```bash
cdk bootstrap  # First time only
cdk deploy
```

## Outputs

After deployment, you'll get:
- API Gateway endpoint URL
- DynamoDB table name
