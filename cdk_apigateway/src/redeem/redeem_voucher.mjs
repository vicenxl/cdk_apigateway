import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, UpdateCommand, GetCommand, QueryCommand } from "@aws-sdk/lib-dynamodb";

const client = new DynamoDBClient({});
const docClient = DynamoDBDocumentClient.from(client);

export const handler = async (event) => {
    console.log('Event received:', JSON.stringify(event));
    const code = event.code;

    try {
        if (typeof code !== 'string' || code.trim() === '') 
            throw new Error('The field "code" is required for redemption!!');

        const tableName = process.env.TABLE_NAME;
        if (!tableName) {
            throw new Error('Environment variable TABLE_NAME is not set.');
        }
        console.log(`Table Name(ENV): ${tableName}`);

        // Step 1: Query the table to get the `creationDate`
        const queryCommand = new QueryCommand({
            TableName: tableName,
            KeyConditionExpression: "voucherID = :voucherID",
            ExpressionAttributeValues: {
                ":voucherID": code,
            },
        });

        const queryResponse = await docClient.send(queryCommand);

        if (queryResponse.Items.length === 0) {
            return {
                statusCode: 404,
                body: JSON.stringify({
                    message: 'Voucher not found!!',
                }),
            };
        }

        // Use the first matched creationDate
        const creationDate = queryResponse.Items[0].creationDate;
        console.log(`Found creationDate for voucher: ${creationDate}`);

        // Step 2: Update the voucher
        const updateCommand = new UpdateCommand({
            TableName: tableName,
            Key: {
                voucherID: code,
                creationDate: creationDate, // Include Sort Key
            },
            UpdateExpression: 'SET #status = :status, dateRedemption = :dateRedemption',
            ExpressionAttributeNames: {
                '#status': 'status',
            },
            ExpressionAttributeValues: {
                ':status': 'redeemed',
                ':dateRedemption': new Date().toISOString(),
                ':activeStatus': 'active',
            },
            ConditionExpression: 'attribute_exists(voucherID) AND #status = :activeStatus',
            ReturnValues: 'ALL_NEW',
        });

        console.log('Redeeming voucher in DynamoDB with voucherID:', code);
        console.log('UpdateCommand:', JSON.stringify(updateCommand));
        const updateResponse = await docClient.send(updateCommand);

        console.log('Voucher redeemed successfully: ', JSON.stringify(updateResponse.Attributes));

        return {
            statusCode: 200,
            body: JSON.stringify({
                message: 'Voucher redeemed successfully!!',
                voucher: updateResponse.Attributes,
            }),
        };
    } catch (error) {
        console.error('Error:', error);
        let statusCode = 500;
        let message = 'Error processing request';
        let voucherDetails = null;

        if (error.name === 'ConditionalCheckFailedException') {
            statusCode = 400;
            message = 'Voucher cannot be redeemed. It may not exist or is already redeemed.';

            // Fetch the voucher details
            try {
                const queryCommand = new QueryCommand({
                    TableName: tableName,
                    KeyConditionExpression: "voucherID = :voucherID",
                    ExpressionAttributeValues: {
                        ":voucherID": code,
                    },
                });

                const queryResponse = await docClient.send(queryCommand);
                voucherDetails = queryResponse.Items[0] || null;
            } catch (getError) {
                console.error('Error fetching voucher details:', getError);
            }
        }

        return {
            statusCode: statusCode,
            body: JSON.stringify({
                message: message,
                error: error.message,
                voucher: voucherDetails,
            }),
        };
    }
};
