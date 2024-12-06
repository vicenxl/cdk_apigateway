from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    BundlingOptions,
    Stack)
from constructs import Construct
from cdk_apigateway.voucher_table import VoucherTable

class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, handler_file: str, path_l: str, function_name: str,table: VoucherTable= None, environment: str=None, **kwargs):
        super().__init__(scope, id)
    
        self.lambda_function = lambda_.Function(
            self,
            "LambdaFunction",
            runtime=lambda_.Runtime.NODEJS_22_X,
            handler=f"{handler_file.split('.')[0]}.handler",
            code=lambda_.Code.from_asset(
                path=path_l),
            function_name=function_name,
            environment=environment,
            **kwargs
        )

        # Agregar permisos para DynamoDB
        if table:
            table.table.grant_read_write_data(self.lambda_function)
            print(f"Added policy for table ARN: {table.table.table_arn}")

