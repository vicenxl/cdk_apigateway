import aws_cdk as core
import aws_cdk.assertions as assertions

from cdk_apigateway.cdk_apigateway_stack import CdkApigatewayStack
from cdk_apigateway.voucher_table import VoucherTable
from cdk_apigateway.lambda_construct import LambdaConstruct
from aws_cdk.assertions import Match
from cdk_apigateway.api_gateway_construct import ApiGatewayConstruct

# example tests. To run these tests, uncomment this file along with the example
# resource in cdk_apigateway/cdk_apigateway_stack.py
def test_lambda_created():
    app = core.App()
    #stack = CdkApigatewayStack(app, "cdk-apigateway") ESTE SI QUISIERA PROBAR EL STACK PRINCIPAL
    stack = core.Stack(app, "TestStack")

    table_name = "vouchers"

    # Crear la Lambda usando el constructor
    LambdaConstruct(
        stack,
        "TestLambda",
        handler_file="index.mjs",
        function_name="voucherGeneratorLambda", 
        table_name=table_name
    )    

    # Crear una representación de la plantilla generada
    template = assertions.Template.from_stack(stack)

    all_lambdas = template.find_resources("AWS::Lambda::Function")
    print(all_lambdas)

    # Verificar que se creó exactamente una función Lambda
    template.resource_count_is("AWS::Lambda::Function", 1)

    # Verificar las propiedades específicas de la Lambda
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "index.handler",
        "Runtime": "nodejs22.x",
        "Environment": {
            "Variables": {
                "TABLE_NAME": table_name
            }
        }
    })

    template.has_resource_properties("AWS::IAM::Policy", {
    "PolicyDocument": {
        "Statement": [
            {
                "Action": [
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem"
                ],
                "Effect": "Allow",
                "Resource": Match.object_like({
                    "Fn::Join": [
                        "",
                        [
                            "arn:aws:dynamodb:",
                            {"Ref": "AWS::Region"},
                            ":",
                            {"Ref": "AWS::AccountId"},
                            f":table/{table_name}"
                        ]
                    ]
                })
            }
        ]
    }
    })

def test_api_gateway_construct():
    # Crear un stack de prueba
    app = core.App()
    stack = core.Stack(app, "TestStack")

    # Instanciar el constructor
    api_gateway_construct = ApiGatewayConstruct(stack, "TestApiGateway")

    # Crear una representación de la plantilla generada
    template = assertions.Template.from_stack(stack)

    # Verificar que se crea una función Lambda
    template.resource_count_is("AWS::Lambda::Function", 1)

    # Verificar las propiedades de la función Lambda
    template.has_resource_properties("AWS::Lambda::Function", {
        "Handler": "app.handler",
        "Runtime": "nodejs22.x"
    })

    # Verificar que se crea un API Gateway REST API
    template.resource_count_is("AWS::ApiGateway::RestApi", 1)

    # Verificar las propiedades del API Gateway
    template.has_resource_properties("AWS::ApiGateway::RestApi", {
        "Name": "MyVoucherAPI",
        "Description": "API Gateway Vouchers"
    })

    # Verificar que existe un recurso para "vouchers" con método GET
    template.has_resource_properties("AWS::ApiGateway::Method", {
        "HttpMethod": "GET",
        "ResourceId": assertions.Match.any_value(),
        "RestApiId": assertions.Match.any_value(),
        "AuthorizationType": "CUSTOM"
    })

