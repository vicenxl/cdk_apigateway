from aws_cdk import (
    # Duration,
    Stack,
    aws_apigateway as apigateway,
)
from constructs import Construct
from cdk_apigateway.lambda_construct import LambdaConstruct
from cdk_apigateway.voucher_table import VoucherTable
from cdk_apigateway.api_gateway_construct import ApiGatewayConstruct
from aws_cdk import aws_lambda as _lambda
import logging

class CdkApigatewayStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

         # Crear la tabla DynamoDB usando la clase
        table_name = "vouchers"
        voucher_table = VoucherTable(self, table_name)
        print(f"Table ARN: {voucher_table.table.table_arn}")
        
        # Creamos las lambdas que vamos a usar
        my_lambda1 = LambdaConstruct(
            self,
            "MyCustomLambda1",
            handler_file="new_voucher.mjs",
            function_name="voucherGeneratorLambda",
            table_arn=voucher_table.table.table_arn
        )
        print(f"Lambda ARN: {my_lambda1.lambda_function.function_arn}")

        my_lambda2 = LambdaConstruct(
            self,
            "MyCustomLambda2",
            handler_file="redeem_voucher.mjs",
            function_name="redeemVoucherLambda",  
            table_arn=voucher_table.table.table_arn
        )
        print(f"Lambda ARN: {my_lambda2.lambda_function.function_arn}")

        my_lambda3 = LambdaConstruct(
            self,
            "MyCustomLambda3",
            handler_file="get_voucher_code.mjs",
            function_name="getInfoVoucherByCodeLambda",
            table_arn=voucher_table.table.table_arn
        )
        print(f"Lambda ARN: {my_lambda3.lambda_function.function_arn}")

        lambda_authorizer = LambdaConstruct(
            self,
            "MyCustomAuthorizerVouchers",
            handler_file="apigateway_authorizer.mjs",
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
            apigateway.LambdaIntegration(my_lambda1.lambda_function,proxy=False),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=authorizer
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
                request_templates=mapping_template
            ),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=authorizer
        )
        
        voucher_id.add_method(
            "GET",
            apigateway.LambdaIntegration(
                my_lambda3.lambda_function,
                proxy=False,
                request_templates=mapping_template
            ),
            authorization_type=apigateway.AuthorizationType.CUSTOM,
            authorizer=authorizer
        )
        #logging.info(f"Method GETVOUCHERBYCODE created with authorizer ID: {authorizer.ref}")
        #print(f"Method GETVOUCHERBYCODE created with authorizer ID: {authorizer.ref}")
        
        

