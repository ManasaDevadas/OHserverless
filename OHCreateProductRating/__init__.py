from ast import NamedExpr, Return
from itertools import product
import logging
from datetime import datetime
from sqlite3 import Timestamp
from uuid import uuid4
import azure.functions as func
import requests
import jsonschema
from jsonschema import validate
import azure.cosmos
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey


HOST = 'https://openhackserverless.documents.azure.com:443/'
#config.settings['host']
MASTER_KEY = 'VuL4ChkTWHFYecMeYrpOFAS4s1u9gSjcnQdAH6GiTFyC4ktFJ6v36YhbSk6R6i4rImtUw0ETRFNZKNDs20MNNg=='
DATABASE_ID = 'openhackserverless'
CONTAINER_ID = 'ratings'

def createConnection(HOST,MASTER_KEY,DATABASE_ID,CONTAINER_ID):
    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY} )
    try:
        # setup database for this sample
        db = client.create_database_if_not_exists(id=DATABASE_ID)
        # setup container for this sample
        container = db.create_container_if_not_exists(id=CONTAINER_ID, partition_key=PartitionKey(path='/id', kind='Hash'))
    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))
    return container  
    

def createItem(container,req_body):
    returndict = container.create_item(body=req_body)
    return returndict
      



def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    print("in here")

    id = str(uuid4())
    timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
    
    productschema = {
                "type": "object",
                "properties": {
                "userId": {"type": "string"},
                "productId": {"type": "string"},
                "locationName": {"type": "string"},
                "rating": {"type": "number", "minimum": 0, "maximum": 5},
                "userNotes": {"type": "string"}
                }
            }



    try:
       req_body = req.get_json()
       validate(instance = req_body, schema= productschema)
       #append the id and timestamp to the body
       req_body['id'] = id 
       req_body['timestamp'] = timestamp

    except ValueError as err:
       return func.HttpResponse(f"Invalid request body: {err}", status_code = 404) 

    except jsonschema.exceptions.ValidationError as err:
        print(err)
        err = "Given JSON data is InValid"
        return func.HttpResponse(f"{err}", status_code = 404)

    #Check if userID and ProductID is present
    userId = req_body['userId']
    print(userId)
    checkUser = requests.get('https://serverlessohapi.azurewebsites.net/api/GetUser?userId='+userId)
    if checkUser.status_code == 400:
        return func.HttpResponse(f"User not found", status_code = 404)
    
    productId = req_body['productId']
    print(productId)
    checkProduct = requests.get('https://serverlessohapi.azurewebsites.net/api/GetProduct?productId='+productId)
    if checkProduct.status_code == 400:
        return func.HttpResponse(f"Product not found", status_code = 404)

    container = createConnection(HOST,MASTER_KEY,DATABASE_ID,CONTAINER_ID)
    item = createItem(container, req_body)
    print("item created", item)

    return func.HttpResponse(f"{req_body}", status_code = 200)
    
