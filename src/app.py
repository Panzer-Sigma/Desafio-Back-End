import json
from operations import *

def lambda_handler(event, context):
    operation_type = event.get('info', {}).get('fieldName')
    arguments = event.get('arguments', {})
#users
    if operation_type == 'getUser':
        return get_user(arguments['id'])
    elif operation_type == 'createUser':
        return create_user(arguments)
    elif operation_type == 'updateUser':
        return update_user(arguments)
    elif operation_type == 'deleteUser':
        return delete_user(arguments['id'])
#contracts
    elif operation_type == 'getContract':
        return get_contract(arguments['id'])
    elif operation_type == 'getContractsByUser':
        return get_contractsByUser(arguments['user_id'])
    elif operation_type == 'createContract':
        return create_contract(arguments)
    elif operation_type == 'updateContract':
        return update_contract(arguments)
    elif operation_type == 'deleteContract':
        return delete_contract(arguments['id'])
    else:
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid operation type')
        }





