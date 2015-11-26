from __future__ import print_function, division, absolute_import
import sys
import boto3

print('Loading ...')

def handler(event, context):
    print('####Loading ...Lambda New')
    #sqs = boto3.resource('sqs')
    #queue = sqs.get_queue_by_name(QueueName='monocyte')
    #print(queue.url)
    #print(queue.attributes.get('DelaySeconds'))
    #return True

