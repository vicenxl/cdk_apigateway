// index.mjs

import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, PutCommand, GetCommand, UpdateCommand } from "@aws-sdk/lib-dynamodb";
import { v4 as uuidv4 } from 'uuid';

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

export const handler = async (event) => {
    console.log('Event received:', JSON.stringify(event));
    try {
        
        if (!event || typeof event !== 'object' || typeof event.amount !== 'number' || event.amount <= 0) {
            throw new Error('Invalid input: event must contain a positive "amount".');
        }
        const amount = event.amount;
        const tableName = process.env.TABLE_NAME;
        if (!tableName) {
            throw new Error('Environment variable TABLE_NAME is not set.');
        }
        console.log(`Table Name(ENV): ${tableName}`);

        if (typeof amount !== 'number' || amount <= 0) 
            throw new Error('The field "amount" is invalid!!');

        const voucher = createVoucher(event.amount);        

        const putCommand = new PutCommand({
            TableName: tableName,
            Item: voucher
        });
        console.log('Saving voucher in DynamoDB(tableName ${tableName}):', JSON.stringify(voucher));
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
        return {
            statusCode: error.name === 'ConditionalCheckFailedException' ? 400 : 500,
            body: JSON.stringify({
                message: error.name === 'ConditionalCheckFailedException' 
                    ? 'Voucher cannot be redeemed. It may not exist or is already inactive.' 
                    : 'Error processing request.',
                error: error.message,
            }),
        };
    }
};

function createVoucher(amount) {
    const voucherCode = 'VOUCHER-' + uuidv4().toUpperCase();
    const creationDate = new Date().toISOString();
    const expiryDate = new Date();
    expiryDate.setMonth(expiryDate.getMonth() + 3);

    return {
        voucherID: voucherCode,
        amount,
        status: 'active',
        creationDate,
        expiryDate: expiryDate.toISOString(),
    };
}
