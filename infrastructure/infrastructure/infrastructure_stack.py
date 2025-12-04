from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    RemovalPolicy,
)
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_apigateway as apigw
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from constructs import Construct
import os

class InfrastructureStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # DynamoDB Table
        events_table = dynamodb.Table(
            self, "EventsTable",
            table_name="events-table",
            partition_key=dynamodb.Attribute(
                name="eventId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )
        
        # Lambda Layer for dependencies
        lambda_layer = _lambda.LayerVersion(
            self, "FastAPILayer",
            code=_lambda.Code.from_asset("../backend", 
                exclude=["*.pyc", "__pycache__", "*.md", ".env*", "main.py", "database.py", "models.py"]
            ),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_11],
            description="FastAPI and dependencies"
        )
        
        # Lambda Function
        api_lambda = _lambda.Function(
            self, "EventsAPIFunction",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="main.handler",
            code=_lambda.Code.from_asset("../backend"),
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "DYNAMODB_TABLE_NAME": events_table.table_name,
                "AWS_REGION": self.region,
                "ALLOWED_ORIGINS": "*"
            },
            layers=[lambda_layer]
        )
        
        # Grant DynamoDB permissions
        events_table.grant_read_write_data(api_lambda)
        
        # API Gateway
        api = apigw.LambdaRestApi(
            self, "EventsAPI",
            handler=api_lambda,
            proxy=True,
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization", "Accept"],
                max_age=Duration.hours(1)
            ),
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=200
            )
        )
        
        # Outputs
        CfnOutput(
            self, "APIEndpoint",
            value=api.url,
            description="API Gateway endpoint URL"
        )
        
        CfnOutput(
            self, "DynamoDBTableName",
            value=events_table.table_name,
            description="DynamoDB table name"
        )
