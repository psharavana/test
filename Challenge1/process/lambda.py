import os
import json
import boto3
from datetime import datetime
from dateutil import tz
from botocore.exceptions import ClientError

debugOn = True
sessionName = 'merlin_session'

# These 4 should be parameters
merlinRealtimeProfileDDbTableName = os.environ['merlinRealtimeProfileDDbTableName'] # 
merlinRoleArn = os.environ['merlinRoleArn']                                         #
merlinCollectEventSQSQueueName = os.environ['merlinCollectEventSQSQueueName']  # 
merlinCustEventSQSQueueName = os.environ['merlinCustEventSQSQueueName']  # 

localTzName = os.environ['localTzName']  #'America/Chicago'

try:
	client
	session
	DDBresource
	DDBTable
	SQSresource

except:
	# Create Session if its not cached
	client = boto3.client('sts')
	response = client.assume_role(RoleArn = merlinRoleArn, RoleSessionName = sessionName)
	session = boto3.Session(
		aws_access_key_id = response['Credentials']['AccessKeyId'],
		aws_secret_access_key = response['Credentials']['SecretAccessKey'],
		aws_session_token = response['Credentials']['SessionToken'])

	if debugOn:
		print("account:" + str(session.client('sts').get_caller_identity()['Account']))

	DDBresource = session.resource('dynamodb')
	SQSresource = session.resource('sqs')
	merlinRealtimeProfileDDBTable = DDBresource.Table(merlinRealtimeProfileDDbTableName)
	merlinCollectEventSqsQueue = SQSresource.get_queue_by_name(QueueName=merlinCollectEventSQSQueueName)
	merlinCustEventsSqsQueue = SQSresource.get_queue_by_name(QueueName=merlinCustEventSQSQueueName)


def converToLocalTime( UTCstr ):
	if UTCstr == '':
		return ''
	else:
		#Convert a UTC datetime string in format  YYYY-MM-DD'T'HH:MI:SS.mmmZ e.g. "2019-12-03T09:44:27.000Z"
			
		fromZone = tz.tzutc()
		toZone   = tz.gettz('America/Chicago') #To-Do - Make this configurable

		# utc = datetime.utcnow()
		utcDateTime = datetime.strptime( UTCstr, '%Y-%m-%dT%H:%M:%S.%fZ')

	
		# Tell the datetime object that it's in UTC time zone since 
		# datetime objects are 'naive' by default
		utcDateTime = utcDateTime.replace(tzinfo=fromZone)   

		# Convert time zone
		localDateTime = utcDateTime.astimezone(toZone)
		localStr      = datetime.strftime( localDateTime, '%Y-%m-%dT%H:%M:%S.%f')
		localStr      = localStr[:23]+"Z"
		
		if debugOn:
			print("UTC date: "+UTCstr+" UTC zone: " +str( utcDateTime.tzname() )+" => Converted to Local date: "+localStr + " Local zone: " + str( localDateTime.tzname() ))
			
		return localStr

def create_outbound_merlin_sqs_collect_event_from_record(record):
	dynamoDBData = record['dynamodb']
	newDynamoDBData = dynamoDBData['NewImage']
	dpk = str(newDynamoDBData['dpk']['N'])
	change_date = newDynamoDBData['change_date']['S']
	change_date_local = converToLocalTime( change_date )
	event_type = newDynamoDBData['event_type']['S']
	digitalData = { 'digitalData': 
		{
			'unencrypted_user_id': dpk,
			'event_type': 'iLottery',
			'event_details': event_type,
			'tsUTC': change_date,
			'tsLocale': change_date_local
		}
	}
	return json.dumps(digitalData)

def create_outbound_ddb_item_from_record(record):
	event_type = 'RELOAD'
	last_state_change = 'UNK'
	version = '-1'
	
	dynamoDBData = record['dynamodb']
	newDynamoDBData = dynamoDBData['NewImage']
	dpk = str(newDynamoDBData['dpk']['N'])
	standard = newDynamoDBData['standard']['S']
	custom = newDynamoDBData['custom']['S']
	change_date = newDynamoDBData['change_date']['S']
	if 'event_type' in newDynamoDBData:
		event_type = newDynamoDBData['event_type']['S']
	if 'last_state_change' in newDynamoDBData:
		last_state_change = newDynamoDBData['last_state_change']['S']
	if 'version' in newDynamoDBData:
		version = newDynamoDBData['version']['S']
	standard = standard.replace("'", "\"")
	custom   = custom.replace("'", "\"")
	standardDict = json.loads( standard )
	customDict   = json.loads( custom )
	change_date                         = converToLocalTime( change_date )
	standardDict['cusChangeTimestamp']      = converToLocalTime( standardDict.get( 'cusChangeTimestamp','') )
	standardDict['cusDateFullyRegistered']  = converToLocalTime( standardDict.get( 'cusDateFullyRegistered','') )          
	standardDict['cusDateLiteRegistered']   = converToLocalTime( standardDict.get( 'cusDateLiteRegistered','') ) 
	customDict['changeTimestamp']           = converToLocalTime( customDict.get( 'changeTimestamp','' ) )
	standard = json.dumps( standardDict )
	custom   = json.dumps( customDict )
	item = {
				'dpk': dpk,
				'timestamp': change_date,
				'profile': standard,
				'custom': custom,
				'event_type': event_type,
				'version': version
			}
	return item

def send_merlin_sqs_collect_event_from_record(record):
	return_val = {
			'statusCode': 200,
			'body': 'OK'
			}	
	try:
		print('Processing Inbound DDB Record: ' + str(record))
		sqs_message = create_outbound_merlin_sqs_collect_event_from_record(record)
	
	except ClientError as e:
		msg = 'DynamoDB stream read ERROR Message:' + e.response['Error']['Message']
		print( msg )
		return_val['statusCode']= 500
		return_val['body'] = msg
		
	else:
		if debugOn:
			print('Adding following record to SQS item:' + str(sqs_message))
		try:
			# Merlin table a little different to dev because ?
			response = merlinCollectEventSqsQueue.send_message(MessageBody = sqs_message)

			httpResponse = int( response['ResponseMetadata']['HTTPStatusCode'] )
			
			# Check for a failure response
			if httpResponse > 299:
				msg = "DynamoDB put Unexpected Response FROM SQS:" + merlinCollectEventSQSQueueName + " httpResponse:"  + str(httpResponse) 
				print( msg )
				return_val['statusCode']= httpResponse
				return_val['body'] = msg

		except ClientError as e:
			msg = 'SQS send ERROR FROM Queue:' + merlinCollectEventSQSQueueName + ' Message:' + e.response['Error']['Message']
			print( msg )
			return_val['statusCode']= 500
			return_val['body'] = msg
		
	return return_val
	
def send_merlin_sqs_cust_event_from_record(record):
	return_val = {
			'statusCode': 200,
			'body': 'OK'
			}	
	try:
		print('Processing Inbound DDB Record: ' + str(record))
		sqs_message = json.dumps(record)
	
	except ClientError as e:
		msg = 'DynamoDB stream read ERROR Message:' + e.response['Error']['Message']
		print( msg )
		return_val['statusCode']= 500
		return_val['body'] = msg
		
	else:
		if debugOn:
			print('Adding following record to SQS item:' + str(sqs_message))
		try:
			# Merlin table a little different to dev because ?
			response = merlinCustEventsSqsQueue.send_message(MessageBody = sqs_message)

			httpResponse = int( response['ResponseMetadata']['HTTPStatusCode'] )
			
			# Check for a failure response
			if httpResponse > 299:
				msg = "DynamoDB put Unexpected Response FROM SQS:" + merlinCustEventSQSQueueName + " httpResponse:"  + str(httpResponse) 
				print( msg )
				return_val['statusCode']= httpResponse
				return_val['body'] = msg

		except ClientError as e:
			msg = 'SQS send ERROR FROM Queue:' + merlinCustEventSQSQueueName + ' Message:' + e.response['Error']['Message']
			print( msg )
			return_val['statusCode']= 500
			return_val['body'] = msg
		
	return return_val
	
	
	
	
def update_merlin_ddb_table_from_record(record):
	return_val = {
			'statusCode': 200,
			'body': 'OK'
			}	
	try:
		print('Processing DDB Streaming record: ' + str(record))
		ddb_item = create_outbound_ddb_item_from_record(record)
	
	except ClientError as e:
		msg = 'DynamoDB stream read ERROR Message:' + e.response['Error']['Message']
		print( msg )
		return_val['statusCode']= 500
		return_val['body'] = msg
		
	else:
		if debugOn:
			print('Putting record into target ddb Table, item:' + str(ddb_item))
		try:
			# Merlin table a little different to dev because ?
			response = merlinRealtimeProfileDDBTable.put_item(Item = ddb_item)

			httpResponse = int( response['ResponseMetadata']['HTTPStatusCode'] )
			
			# Check for a failure response
			if httpResponse > 299:
				msg = "DynamoDB put Unexpected Response FROM table:" + merlinRealtimeProfileDDbTableName + " httpResponse:"  + str(httpResponse) 
				print( msg )
				return_val['statusCode']= httpResponse
				return_val['body'] = msg

		except ClientError as e:
			msg = 'DynamoDB put ERROR FROM table:' + merlinRealtimeProfileDDbTableName + ' Message:' + e.response['Error']['Message']
			print( msg )
			return_val['statusCode']= 500
			return_val['body'] = msg
		
	return return_val


def lambda_handler(event, context):
	recordCount = 0
	ddb_item = None
	sqs_item = None
	return_val = { 
		'statusCode': 500,
		'body': 'Unknown Error'
		}
	
	for record in event['Records']:
		return_val = send_merlin_sqs_cust_event_from_record(record)
		#return_val = update_merlin_ddb_table_from_record(record)
		#if return_val['statusCode'] == 200:
		#	return_val = send_merlin_sqs_collect_event_from_record(record)
	
	return return_val	

