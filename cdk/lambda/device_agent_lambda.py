import json
import random
import boto3
import os

#dynamo client
dynamodb = boto3.client('dynamodb')
#tableName = 'flux3000-feature-requests'
tableName = os.environ['TABLE_NAME']

#sns client
sns = boto3.client('sns')
# get topic arn from environment variable
topicarn = os.environ['TOPIC_ARN']
#topicarn = 'arn:aws:sns:us-west-2:161615149547:FeatureRequests'

def get_named_parameter(event, name):

    return next(item for item in event['parameters'] if item['name'] == name)['value']

def get_named_property(event, name):
    return next(item for item in event['requestBody']['content']['application/json']['properties'] if item['name'] == name)['value']

def createFeatureRequest(event):
    print("calling method: create feature request")
    featureRequestName = get_named_parameter(event, 'featureRequestName')
    featureRequestDescription = get_named_parameter(event, 'featureRequestDescription') 
    customerName = get_named_parameter(event, 'customerName') 
    
    print (event)
    
    # TODO: implement creating featureRequest
    featureRequestID = str(random.randint(1, 99999))

    
    item = {
        'featureRequestID': {"S": featureRequestID},
        'featureRequestName': {"S": featureRequestName},
        'featureRequestDescription': {"S": featureRequestDescription},
        'customerName': {"S": customerName}
        }

    dynamodb.put_item(
        TableName=tableName,
        Item=item
        )
    
    response = sns.publish(
        TopicArn=topicarn,
        Message=f"your feature request {featureRequestName} has been created and assigned to trevx@amazon.com",
        Subject="Feature Request Successfully Created"
    )
    
    print(response['MessageId']) 


    return {
        'body': f"Created request {featureRequestID} in {tableName}"
    }

def updateFeatureRequest(event):
    print(event)
    
    featureRequestID = str(get_named_parameter(event, 'featureRequestID'))
    customerName = get_named_parameter(event, 'customerName')
    

    # TODO: impliment delete from dynamo here?
    key = {
        'featureRequestID': {"S": featureRequestID},
        }

    attribute_updates = {
        'customerName': {'Value': {'S': customerName}}
    }

    dynamodb.update_item(
        TableName=tableName,
        Key=key,
        AttributeUpdates=attribute_updates
    )

    response = sns.publish(
        TopicArn=topicarn,
        Message=f"your feature request {featureRequestID} has been updated by trevx@amazon.com",
        Subject="Feature Request Successfully Updated"
    )

    print(response['MessageId']) 

    # Return a success message
    return { 
        'body': f"Updated request {featureRequestID} in {tableName}"
    }

    
def lambda_handler(event, context):

    result = ''
    response_code = 200
    action_group = event['actionGroup']
    api_path = event['apiPath']

    print("DEBUG: Lambda event ", str(event))
    print("DEBUG: Lambda context ", str(context))

    print ("lambda_handler == > api_path: ",api_path)
    
    if api_path == '/createFeatureRequest':
        result = createFeatureRequest(event)
    elif api_path == '/updateFeatureRequest':
        result = updateFeatureRequest(event)
    else:
        response_code = 404
        result = f"Unrecognized api path: {action_group}::{api_path}"

    response_body = {
        'application/json': {
            'body': json.dumps(result)
        }
    }
    
    print ("Event:", event)
    action_response = {
        'actionGroup': event['actionGroup'],
        'apiPath': event['apiPath'],
        # 'httpMethod': event['HTTPMETHOD'], 
        'httpMethod': event['httpMethod'], 
        'httpStatusCode': response_code,
        'responseBody': response_body
    }

    api_response = {'messageVersion': '1.0', 'response': action_response}
        
    return api_response