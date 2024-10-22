import os
import uuid
from datetime import datetime
from decimal import Decimal
import boto3
from botocore.exceptions import ClientError

# pega envs definidas no yaml
users_table_name = os.environ['Users_Table']
contracts_table_name = os.environ['Contracts_Table']

#chama para interagir com o dynamo pelo boto3
dynamodb = boto3.resource('dynamodb')

# Obtém referências para as tabelas do DynamoDB
users_table = dynamodb.Table(users_table_name)
contracts_table = dynamodb.Table(contracts_table_name)


class CustomError(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.message)

def get_user(user_id):
    try:
        response = users_table.get_item(Key={'id': user_id}) 
        user_data = response.get('Item')
        if user_data is None or ''  or []:
            return None   
        return {
                'id': user_data['id'],
                'name': user_data['name'],
                'email': user_data['email']
            }
    
    except CustomError as e:
        # Handle custom errors like validation or "user not found" errors
        return {
            'statusCode': e.code,
            'message': e.message
        }
    
    except ClientError as e: 
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': error_code,
            'message': error_message
        }
       
    except Exception as e:
        return {
            'statusCode': 500,
            'message': 'An unexpected error occurred',
            'details': str(e)
        }
    
def create_user(args):
    try:
        user_data = {
            'id': args['input'].get('id', str(uuid.uuid4())),
            'name': args['input']['name'],
            'email': args['input']['email']
        }
        users_table.put_item(Item=user_data)
        return {
            'id': user_data['id'],
            'name': args['input']['name'],
            'email': args['input']['email']
        }

    except ClientError as e: 
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': error_code,
            'message': error_message
        }
       
    except Exception as e:
        return {
            'statusCode': 500,
            'message': 'An unexpected error occurred',
            'details': str(e)
        }
    
def update_user(args):
    user_id = args.get('id')
    input_data = args.get('input')
    try:
        updateCommand = "set" 
        expnames = { }
        expvalues = { }
        if input_data.get('name') is not None:
            updateCommand += " #name = :name,"
            expnames["#name"] = "name"
            expvalues[":name"] = input_data.get('name')
            
        if input_data.get('email') is not None:
            updateCommand +=  " #email = :email,"
            expnames["#email"] = "email"
            expvalues[":email"] = input_data.get('email')
        updateCommand = updateCommand.rstrip(',')

        response = users_table.update_item(
            Key={'id': user_id},
            UpdateExpression=updateCommand,
            ExpressionAttributeNames=expnames,
            ExpressionAttributeValues=expvalues,
            ReturnValues="ALL_NEW"  # Returns the updated values
        )
        
        return {
            'id': response['Attributes']['id'],
            'name': response['Attributes']['name'],
            'email': response['Attributes']['email']
        }

    
    except ClientError as e: 
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': error_code,
            'message': error_message
        }
       
    except Exception as e:
        return {
            'statusCode': 500,
            'message': 'An unexpected error occurred',
            'details': str(e)
        }

def update_contract(args):
    print("updatecontractAARGS")
    print(args)
    contract_id = args.get('id')
    input_data = args.get('input')
    try:
        updateCommand = "set" 
        expnames = { }
        expvalues = { }
        user_id = None
        if input_data.get('user_id') is not None:
            updateCommand += " #user_id = :user_id,"
            expnames["#user_id"] = "user_id"
            expvalues[":user_id"] = input_data.get('user_id')
            user_id = input_data.get('user_id')

        if input_data.get('description') is not None:
            updateCommand += " #description = :description,"
            expnames["#description"] = "description"
            expvalues[":description"] = input_data.get('description')

        if input_data.get('created_at') is not None:
            updateCommand += " #created_at = :created_at,"
            expnames["#created_at"] = "created_at"
            expvalues[":created_at"] = input_data.get('created_at')

        if input_data.get('fidelity') is not None:
            updateCommand += " #fidelity = :fidelity,"
            expnames["#fidelity"] = "fidelity"
            expvalues[":fidelity"] = input_data.get('fidelity')

        if input_data.get('amount') is not None:
            amountupdate = Decimal(str(input_data.get('amount')))
            updateCommand += " #amount = :amount,"
            expnames["#amount"] = "amount"
            expvalues[":amount"] = amountupdate

        updateCommand = updateCommand.rstrip(',')

        response = contracts_table.update_item(
                Key={'id': contract_id},
                UpdateExpression=updateCommand,
                ExpressionAttributeNames=expnames,
                ExpressionAttributeValues=expvalues,
                ReturnValues="ALL_NEW"  # Returns the updated values
            )
        print("contracts_table-result:")
        print(response)
        return {
            'id': response['Attributes']['id'],
            'description' : response['Attributes']['description'],
            'user_id': response['Attributes']['user_id'],
            'created_at': response['Attributes']['created_at'],
            'fidelity': response['Attributes']['fidelity'],
            'amount': float(response['Attributes']['amount'])
        }

    except ClientError as e:
        print("getupdatescontractClientError")
        print(e)
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': error_code,
            'message': error_message
        }
       
    except Exception as e:
        print("getcontractsException")
        print(e)
        return {
            'statusCode': 500,
            'message': 'An unexpected error occurred',
            'details': str(e)
        }

def delete_user(user_id):
    print(user_id)
    try:
        usercontracts = get_contractsByUser(user_id)
        if "Contracts" in usercontracts:
            if usercontracts["Contracts"] != []:
                return {
                    "success": False,
                    "message": "Cannot delete user with contracts!"
                }
    
        response = users_table.delete_item(Key={'id': user_id}, ReturnValues="ALL_OLD") 
        print("response")
        print(response)
        
        if "Attributes" in response:
            return {
                "success": True,
                "message": "User deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": "Unexisting user"
            }

    
    except ClientError as e:
        print("deleteuserClientError")
        print(e)
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            "success": False,
            "message": "Unexisting user"
        }
    
       
    except Exception as e:
        print(  "deleteuserException")
        print(e)
        return {
            "success": False,
            "message": "Unexisting user"
        }
    
    
# Funções para manipulação dos contratos
def get_contract(contract_id):
    try:
        response = contracts_table.scan(FilterExpression='id = :id',
            ExpressionAttributeValues={':id': contract_id}
        )
        items = response.get('Items', [])
        if items:
            resobj = items[0]
            user_id = items[0]['user_id']
            userdata = get_user(user_id)
            resobj["user"] = userdata
            return resobj
        else: 
            return None 
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': error_code,
            'message': error_message
        }
       
    except Exception as e:
        return {
            'statusCode': 500,
            'message': 'An unexpected error occurred',
            'details': str(e)
        }
    
def get_contractsByUser(user_id):
    print(user_id)
    try:
        response = contracts_table.scan(FilterExpression='user_id = :user_id', ExpressionAttributeValues={':user_id': user_id}) 
        print("getbyuser-response")
        print(response)
        token = ""
        if 'LastEvaluatedKey' in response:
            token = response["LastEvaluatedKey"]
        contractsresponse = response.get('Items', [])
        print(contractsresponse)
        return {
            "Contracts": contractsresponse,
            "nextToken": token
        }
            
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': error_code,
            'message': error_message
        }
       
    except Exception as e:
       return {
            'statusCode': 500,
            'message': 'An unexpected error occurred',
            'details': str(e)
        }
    
def create_contract(args):
    try:
        amount = Decimal(str(args['input']['amount']))
        contract_data = {
            'id': args['input'].get('id', str(uuid.uuid4())),
            'description': args['input']['description'],
            'user_id': args['input']['user_id'],
            'created_at': args['input'].get('created_at', str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))),
            'fidelity': args['input']['fidelity'],
            'amount': amount
        }
        contracts_table.put_item(Item=contract_data)
        return contract_data
    
    except ClientError as e: 
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            'statusCode': error_code,
            'message': error_message
        }
       
    except Exception as e:
        return {
            'statusCode': 500,
            'message': 'An unexpected error occurred',
            'details': str(e)
        }
    

    
def delete_contract(contract_id):
    try:
        response = contracts_table.delete_item(Key={'id': contract_id}, ReturnValues="ALL_OLD")
        if "Attributes" in response:
            return {
                "success": True,
                "message": "Contract deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": "Unexisting Contract!"
            }
    
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        return {
            "success": False,
            "message": "Unexisting contract"
        }
    
       
    except Exception as e:
        return {
            "success": False,
            "message": "Unexisting contract"
        }
    
    
