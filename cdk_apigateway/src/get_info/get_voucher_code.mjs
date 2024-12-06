import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand, QueryCommand} from "@aws-sdk/lib-dynamodb";

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

        const queryCommand = new QueryCommand({
            TableName: tableName,
            KeyConditionExpression: "voucherID = :voucherID",
            ExpressionAttributeValues: {
                ":voucherID": code,
            },
        });
        console.log('Checking voucher code:', code);
        console.log('QueryCommand:', JSON.stringify(queryCommand));

        const queryResponse = await docClient.send(queryCommand);

        // Handle case where no items are returned
        if (!queryResponse.Items || queryResponse.Items.length === 0) {
            console.log('No vouchers found for the given code.');
            return {
                statusCode: 404,
                body: JSON.stringify({
                    message: 'Voucher not found!!',
                }),
            };
        }
        console.log('Data voucher returned:', JSON.stringify(queryResponse.Items[0]));

        return {
            statusCode: 200,
            body: JSON.stringify({
            message: 'Voucher retrieved successfully!!',
            voucher: queryResponse.Items[0]
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
