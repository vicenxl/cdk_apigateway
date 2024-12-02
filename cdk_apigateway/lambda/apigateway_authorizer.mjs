
export const handler = async (event) => {
    const token = event.authorizationToken;
    console.log('token received:', token);
    console.log('Method ARN:', event.methodArn);
  
    if (!token) {
      console.log('ERROR: no token received!!');
      return generatePolicy('user', 'Deny', event.methodArn);
    }
    
    //const expectedToken = process.env.EXPECTED_TOKEN;
    const expectedToken = "valid-token";
  
    if (token === expectedToken) 
        return generatePolicy('user', 'Allow', event.methodArn);
    else
        return generatePolicy('user', 'Deny', event.methodArn);
  };
  
  function generatePolicy(principalId, effect, resource) {
    const authResponse = {};
    authResponse.principalId = principalId;
  
    if (effect && resource) {
        const policyDocument = {
            Version: '2012-10-17',
            Statement: [
                {
                    Action: 'execute-api:Invoke',
                    Effect: effect,
                    Resource: resource
                }
            ]
        };
        authResponse.policyDocument = policyDocument;
        console.log('Generated policyDocument:', JSON.stringify(policyDocument, null, 2));
    }
    console.log('Return authResponse:', JSON.stringify(authResponse, null, 2));
    return authResponse;
  }
  