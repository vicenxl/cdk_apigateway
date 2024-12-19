
# CDK API Gateway Project

This project creates a REST API to manage vouchers using AWS infrastructure. It leverages the AWS CDK to provision resources like API Gateway, Lambda, and DynamoDB.

## Features

- **DynamoDB Table**: Stores voucher information with the table name `vouchers`.
- **Lambda Functions**: Handles business logic for creating, reading, updating, and deleting vouchers.
- **API Gateway**: Exposes the Lambda functions as REST endpoints.

## Project Structure

- `cdk_apigateway_stack.py`: Main stack definition, integrating all resources.
- `lambda_construct.py`: Contains reusable constructs for defining Lambda functions.
- `voucher_table.py`: Creates the DynamoDB table resource.
- `api_gateway_construct.py`: Configures the API Gateway.

## Prerequisites

1. Install [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/getting_started.html).
2. Install Python dependencies:

    ```bash
    pip install -r requirements.txt
    ```

3. Configure your AWS credentials.

## Deployment

1. Synthesize the CloudFormation template:

    ```bash
    cdk synth
    ```

2. Deploy the stack:

    ```bash
    cdk deploy
    ```

## API Endpoints

The API exposes the following endpoints:

- `POST /vouchers`: Creates a new voucher.
- `GET /vouchers/{id}`: Retrieves a voucher by ID.
- `PUT /vouchers/{id}`: Updates a voucher by ID.
- `DELETE /vouchers/{id}`: Deletes a voucher by ID.

## Useful Commands

- `cdk ls`: List all stacks in the app.
- `cdk synth`: Synthesize the CloudFormation template.
- `cdk deploy`: Deploy the app to your AWS account.
- `cdk destroy`: Remove the stack from your AWS account.

## Notes

- Ensure your AWS account has the necessary permissions to deploy the resources.
- Modify `environment` variables in `cdk_apigateway_stack.py` to adapt to your region or table name.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
