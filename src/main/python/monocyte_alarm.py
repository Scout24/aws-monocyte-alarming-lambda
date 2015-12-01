from __future__ import print_function, division, absolute_import
import datetime
import boto3
import json

USOFA_KEY = 'accounts.json'
REGION_NAME = 'eu-west-1'
USOFA_BUCKET = 'is24-accounts'


class MonocyteAlarm(object):

    def __init__(self, sqs_queue, sender_email, recipients, dry_run=True):
        self.sqs_queue = sqs_queue
        self.sender_email = sender_email
        self.recipients = recipients
        self.dry_run = dry_run

    def __call__(self):
        reported_accounts = self.get_accounts_from_sqs()
        accounts = self.get_usofa_data(USOFA_BUCKET)
        usofa_aliases = {aliases for aliases in accounts.iterkeys()}
        # in usofa but not in sqs queue
        usofa_accounts = usofa_aliases.difference(reported_accounts)
        # in sqs but not in usofa
        sqs_accounts = reported_accounts.difference(usofa_aliases)
        body = self._email_body(usofa_accounts, sqs_accounts)
        self._send_email(self.sender_email, self.recipients, body)

    def get_accounts_from_sqs(self):
        sqs = boto3.resource('sqs', REGION_NAME)
        queue = sqs.get_queue_by_name(QueueName=self.sqs_queue)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        reported_accounts = set()
        while True:
            messages = queue.receive_messages(AttributeNames=['All'], MaxNumberOfMessages=10)
            for message in messages:
                sent_time = int(float(message.attributes['SentTimestamp'])) / 1000.
                sent_time = datetime.datetime.fromtimestamp(sent_time)
                if sent_time >= yesterday:
                    encoded_body = json.loads(message.body)
                    reported_accounts.add(encoded_body['account'])
                else:
                    if not self.dry_run:
                        message.delete()
            if not messages:
                break
        return reported_accounts

    def _email_body(self, usofa_accounts, sqs_accounts):
        body = '''Dear AWS User,\n
our Monocyte Alarming identified some suspicious account behaviour during the last 24 hours.\n
Account in AWS account list (Usofa) but monocyte didn't run in this account:'''
        body += '\n\t' + '\n\t'.join(usofa_accounts)
        body += '\n\nAccounts not in AWS account list (Usofa) but monocyte ran successfully in this account:\n'
        body += '\n\t' + '\n\t'.join(sqs_accounts)
        body += '\n\nBest,\n\tYour Compliance Team'
        return body

    def _send_email(self, sender_email, recipients, body):
        conn = boto3.client('ses')
        conn.send_email(
            Source=sender_email,
            Message={'Subject': {'Data': 'Monocyte Alarming', 'Charset': 'utf-8'},
                     'Body': {'Text': {'Data': body, 'Charset': 'utf-8'}}},
            Destination={'ToAddresses': recipients})

    def get_usofa_data(self, usofa_bucket_name):
        s3_connection = boto3.resource('s3', REGION_NAME)
        key = s3_connection.Object(usofa_bucket_name, USOFA_KEY)
        account_data = json.loads(key.get()['Body'].read().decode('utf-8'))
        return account_data
