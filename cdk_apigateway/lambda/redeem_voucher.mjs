// index.mjs

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, UpdateCommand } from "@aws-sdk/lib-dynamodb";
import { v4 as uuidv4 } from 'uuid';

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

export const handler = async (event) => {
    console.log('Event received:', JSON.stringify(event));
    try {
        const code = event.code;

        if (typeof code !== 'string' || code.trim() === '') 
            throw new Error('The field "code" is required for redemption!!');

        const updateCommand = new UpdateCommand({
            TableName: 'vouchers',
            Key: {
                code: code
            },
            UpdateExpression: 'SET #status = :status, dateRedemption = :dateRedemption',
            ExpressionAttributeNames: {
            '#status': 'status'
            },
            ExpressionAttributeValues: {
                ':status': 'inactive',
                ':dateRedemption': new Date().toISOString(),
                ':activeStatus': 'active'
            },
            ConditionExpression: 'attribute_exists(code) AND #status = :activeStatus',
            ReturnValues: 'ALL_NEW'
        });

        console.log('Redeeming voucher in DynamoDB with code:', code);
        const updateResponse = await docClient.send(updateCommand);

        console.log('Voucher redeemed successfully: ', JSON.stringify(updateResponse.Attributes));

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Voucher redeemed successfully!!',
                voucher: updateResponse.Attributes
            }),
        };
    } catch (error) {
        console.error('Error:', error);
        let statusCode = 500;
        let message = 'Error processing request';

        if (error.name === 'ConditionalCheckFailedException') {
            statusCode = 400;
            message = 'Voucher cannot be redeemed. It may not exist or is already inactive.';
        }

        return {
            statusCode: statusCode,
            body: JSON.stringify({
                message: message,
                error: error.message
            }),
        };
    }
};