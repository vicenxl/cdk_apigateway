from aws_cdk import (
    # Duration,
    Stack,
    aws_apigateway as apigateway
)
from constructs import Construct
from cdk_apigateway.lambda_construct import LambdaConstruct
from cdk_apigateway.voucher_table import VoucherTable
from cdk_apigateway.api_gateway_construct import ApiGatewayConstruct

class CdkApigatewayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

         # Crear la tabla DynamoDB usando la clase
        table_name = "vouchers"
        voucher_table = VoucherTable(self, table_name)
        print(f"Table ARN: {voucher_table.table.table_arn}")
        print(f"Table NAME: {voucher_table.table.table_name}")

        environment_l = {
            "TABLE_NAME": table_name,
            "REGION": "eu-west-1"
        }
        
        # Creamos las lambdas que vamos a usar
        my_lambda1 = LambdaConstruct(
            self,
            "MyCustomLambda1",
            handler_file="new_voucher.mjs",
            path_l="cdk_apigateway/src/new",
            function_name="voucherGeneratorLambda",
            table=voucher_table,
            environment=environment_l
        )
        print(f"Lambda ARN: {my_lambda1.lambda_function.function_arn}")

        my_lambda2 = LambdaConstruct(
            self,
            "MyCustomLambda2",
            handler_file="redeem_voucher.mjs",
            path_l="cdk_apigateway/src/redeem",
            function_name="redeemVoucherLambda",  
            table=voucher_table,
            environment=environment_l
        )
        print(f"Lambda ARN: {my_lambda2.lambda_function.function_arn}")

        my_lambda3 = LambdaConstruct(
            self,
            "MyCustomLambda3",
            handler_file="get_voucher_code.mjs",
            path_l="cdk_apigateway/src/get_info",
            function_name="getInfoVoucherByCodeLambda",
            table=voucher_table,
            environment=environment_l
        )
        print(f"Lambda ARN: {my_lambda3.lambda_function.function_arn}")

        lambda_authorizer = LambdaConstruct(
            self,
            "MyCustomAuthorizerVouchers",
            handler_file="apigateway_authorizer.mjs",
            path_l="cdk_apigateway/src/auth",
            function_name="apigatewayAuthorizerLambda"
        )
        print(f"Lambda ARN: {lambda_authorizer.lambda_function.function_arn}")

        # Crear el API Gateway Construct
        apigateway_vouchers = ApiGatewayConstruct(self, "MyApiGatewayConstruct")    
        
        #Creamos los recursos
        authorizer = apigateway_vouchers.add_authorizer_v2("MyAuthorizerVoucher", lambda_authorizer.lambda_function)
        vouchers = apigateway_vouchers.api.root.add_resource("vouchers")
        new = vouchers.add_resource("new")
        voucher_id = vouchers.add_resource("{voucherId}")
     
        # Añadir los métodos al API Gateway
        new.add_method(
            "POST", 
            apigateway.LambdaIntegration(
                my_lambda1.lambda_function,
                proxy=False,
                passthrough_behavior=apigateway.PassthroughBehavior.WHEN_NO_MATCH,
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": "$input.body"
                        }
                    )
                ]
            ),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=authorizer,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigateway.Model.EMPTY_MODEL
                    }
                )
            ]
        )
    
        # Crear el mapping template
        mapping_template = {
            "application/json": '{ "code" : "$input.params(\'voucherId\')" }'
        }

        voucher_id.add_method(
            "POST",
            apigateway.LambdaIntegration(
                my_lambda2.lambda_function,
                proxy=False,
                request_templates=mapping_template,
                passthrough_behavior=apigateway.PassthroughBehavior.WHEN_NO_MATCH,
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": "$input.body"
                        }
                    )
                ]
            ),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=authorizer,
            method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigateway.Model.EMPTY_MODEL
                    }
                )
            ]
        )
        
        voucher_id.add_method(
            "GET",
            apigateway.LambdaIntegration(
                my_lambda3.lambda_function,
                proxy=False,
                request_templates=mapping_template,
                integration_responses=[
                    apigateway.IntegrationResponse(
                        status_code="200",
                        response_templates={
                            "application/json": "$input.body"
                        }
                    )
                ]
            ),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=authorizer,
             method_responses=[
                apigateway.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigateway.Model.EMPTY_MODEL
                    }
                )
            ]
        )   
