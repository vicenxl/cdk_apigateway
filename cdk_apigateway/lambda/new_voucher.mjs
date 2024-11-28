// index.mjs

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand, GetCommand, UpdateCommand } from "@aws-sdk/lib-dynamodb";
import { v4 as uuidv4 } from 'uuid';

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

export const handler = async (event) => {
    console.log('Event received:', JSON.stringify(event));
    try {
        const operationType = event.operationType;
 
        const amount = event.amount;

        if (typeof amount !== 'number' || amount <= 0) 
            throw new Error('The field "amount" is invalid!!');

        const voucherCode = genCodeUnique();

        const voucher = {
            code: voucherCode,
            amount: amount,
            status: 'active',
            creationDate: new Date().toISOString()
        };

        const putCommand = new PutCommand({
            TableName: 'vouchers',
            Item: voucher
        });
            console.log('Saving voucher in DynamoDB(tableName "vouchers"):', JSON.stringify(voucher));
            await docClient.send(putCommand);
            console.log('Voucher saved successfully in DynamoDB!!');

            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: 'Voucher generated successfully!!',
                    voucher: voucher
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

function genCodeUnique() {
    return 'VOUCHER-' + uuidv4().toUpperCase();
}
