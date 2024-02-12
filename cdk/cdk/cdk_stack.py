from aws_cdk import (
    # Duration,
    Stack,
    aws_lambda as _lambda,
    aws_dynamodb as dynamodb,
    aws_sns as sns,
    aws_s3 as s3,
    CfnOutput
)

from constructs import Construct
from aws_cdk import aws_iam as iam

class CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here

        # Create a SNS topic for feature requests
        topic = sns.Topic(self, "device-agent-topic")

        # Create a Feature requests dynamodb table
        table = dynamodb.Table(self, "DeviceAgentTable",
            partition_key=dynamodb.Attribute(name="featureRequestID", type=dynamodb.AttributeType.STRING)
        )

        # Create a lambda execution role 
        lambda_role = iam.Role(self, "LambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com")
        )

        # add permissions to lambda execution role to access dynamodb table and sns topic
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[table.table_arn],
                actions=["dynamodb:*"]
            )
        )

        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                resources=[topic.topic_arn],
                actions=["sns:*"]
            )
        )

        # Add lambda AWSLambdaBasicExecutionRole managed policy to lambda execution role
        lambda_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole"))

        # Create a lambda function to handle feature requests from the lambda directory
        lambda_function = _lambda.Function(self, "DeviceAgentHandler",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="device_agent_lambda.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            role=lambda_role
        )

        # Add a resource based policy to the lambda function
        # Statement ID: agent-invoke-lambda
        # Principal: bedrock.amazonaws.com
        # Action: lambda:InvokeFunction
        # Source ARN: arn:aws:bedrock:<region>:<account_id>:agent/*
        region = self.region
        account_id = self.account
        #principal_arn = f"arn:aws:bedrock:{region}:{account_id}:agent/*"
        #principal = iam.ArnPrincipal(principal_arn)
        principal = iam.ServicePrincipal("bedrock.amazonaws.com")
        lambda_function.add_permission(
            "agent-invoke-lambda",
            principal=principal,
            action="lambda:InvokeFunction"
        )

        # Add a TABLE_NAME environment variable to the lambda function
        lambda_function.add_environment("TABLE_NAME", table.table_name)
        
        # Add a TOPIC_ARN environment variable to the lambda function
        lambda_function.add_environment("TOPIC_ARN", topic.topic_arn)

        # Add an S3 bucket to the stack to hold schema
        bucket = s3.Bucket(self, "bedrock-agent-schema-bucket")

        # Output lambda ARN
        CfnOutput(self, "LambdaArn", value=lambda_function.function_arn)

        # Output bucket name
        CfnOutput(self, "SchemaBucket", value=bucket.bucket_name)

        # Output the AWS CLI command to upload a file to the S3 bucket
        schema_file = "device-agent-schema.json"
        upload_command = f"aws s3 cp {schema_file} s3://{bucket.bucket_name}/{schema_file}"
        CfnOutput(self, "UploadCommandOutput",
                       value=upload_command,
                       description="AWS CLI command to upload a file to the S3 bucket")
    
