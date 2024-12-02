from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
    Stack,
    aws_iam as iam
)
import logging
from constructs import Construct

class ApiGatewayConstruct(Construct):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Crear el API Gateway REST API
        self.api = apigateway.RestApi(
            self, 'MyApiGateway',
            rest_api_name='MyVoucherAPI',
            description='API Gateway Vouchers that managed the logic redemption burning coupons asociated with amounts of money'
        )

    def add_authorizer(self, authorizer_name: str, authorizer_function: _lambda.Function) -> apigateway.CfnAuthorizer:
        """Método para añadir un authorizer"""
         # Obtener la región del stack
        region = Stack.of(self).region
        authorizer = apigateway.CfnAuthorizer(
            self, authorizer_name,
            rest_api_id=self.api.rest_api_id,
            name=authorizer_name,
            type="TOKEN",
            authorizer_uri=f"arn:aws:apigateway:{region}:lambda:path/2015-03-31/functions/{authorizer_function.function_arn}/invocations",
            auth_type="CUSTOM",
            identity_source="method.request.header.Authorization"
        )
        # Agregar un mensaje de registro para depurar el ID del autorizer
        logging.info(f"Authorizer created with ID: {authorizer.ref}")
        print(f"Authorizer created with ID: {authorizer.ref}")
        return authorizer
    
    def add_authorizer_v2(self, authorizer_name: str, authorizer_function: _lambda.Function) -> apigateway.RequestAuthorizer:
        """Método para añadir un authorizer"""
        # Grant API Gateway permission to invoke the Lambda function
        #authorizer_function.add_permission(
        #    "ApiGatewayInvoke",
        #    principal=iam.ServicePrincipal("apigateway.amazonaws.com"),
        #    action="lambda:InvokeFunction"
        #)
        # Create Lambda Authorizer Token Type
        authorizer = apigateway.TokenAuthorizer(
            self, authorizer_name,
            handler=authorizer_function,
            identity_source="method.request.header.Authorization"
        )
        return authorizer

    def add_resource_with_method(self, path: str, method: str, integration: apigateway.Integration, authorizer: apigateway.RequestAuthorizer) -> None:
        """Método para añadir recursos y métodos al API Gateway"""
        new_resource = self.api.root.add_resource(path)
        new_resource.add_method(
            method,
            integration,
            authorization_type=apigateway.AuthorizationType.CUSTOM if authorizer else apigateway.AuthorizationType.NONE,
            authorizer=authorizer
        )       
