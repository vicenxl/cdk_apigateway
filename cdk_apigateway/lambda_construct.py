from aws_cdk import ( aws_lambda as lambda_, Stack)
from constructs import Construct

from aws_cdk import aws_iam as iam

class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, handler_file: str, function_name: str, table_arn: str = None, **kwargs):
        super().__init__(scope, id)

        environment = {
            "TABLE_NAME": table_arn.split(":")[-1].split("/")[-1] if table_arn else "vouchers",
            "REGION": "eu-west-1"
        }

        self.lambda_function = lambda_.Function(
            self,
            "LambdaFunction",
            runtime=lambda_.Runtime.NODEJS_22_X,
            handler=f"{handler_file.split('.')[0]}.handler",
            code=lambda_.Code.from_asset("cdk_apigateway/lambda"),
            function_name=function_name,
            environment=environment,
            **kwargs
        )

        # Agregar permisos para DynamoDB
        if table_arn:
            print(f"Adding policy for table ARN: {table_arn}")
            self.lambda_function.add_to_role_policy(iam.PolicyStatement(
                actions=["dynamodb:PutItem", "dynamodb:GetItem", "dynamodb:UpdateItem"],
                resources=[table_arn]
            ))
