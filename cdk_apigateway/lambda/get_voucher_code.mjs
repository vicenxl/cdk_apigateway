import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

export const handler = async (event) => {
    console.log('Event received:', JSON.stringify(event));
    try {
        const code = event.code;

        if (typeof code !== 'string' || code.trim() === '') 
            throw new Error('The field "code" is required for querying!!');

        const tableName = process.env.TABLE_NAME;
        if (!tableName) {
            throw new Error('Environment variable TABLE_NAME is not set.');
        }
        console.log(`Table Name(ENV): ${tableName}`);

        const getCommand = new GetCommand({
            TableName: tableName,
            Key: {voucherID: code}
        });
        console.log('Checking voucher code in :', code);
        console.log('GetCommand:', JSON.stringify(getCommand));
        const getResponse = await docClient.send(getCommand);

        if (!getResponse.Item) {
            return {
                statusCode: 404,
                body: JSON.stringify({
                message: 'Voucher not found!!'
                }),
            };
        }
        console.log('Data voucher returned:', JSON.stringify(getResponse.Item));

        return {
            statusCode: 200,
            body: JSON.stringify({
            message: 'Voucher retrieved successfully!!',
            voucher: getResponse.Item
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
