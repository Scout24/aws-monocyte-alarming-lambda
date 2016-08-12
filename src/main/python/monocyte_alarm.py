from __future__ import print_function, division, absolute_import

import datetime
import boto3
import json

from pils import dict_is_subset


class MonocyteAlarm(object):

    def __init__(self, sqs_queue, sender_email, recipients, usofa_key, usofa_bucket, usofa_filter, region_name):
        self.sqs_queue = sqs_queue
        self.sender_email = sender_email
        self.recipients = recipients
        self.usofa_key = usofa_key
        self.usofa_bucket = usofa_bucket
        self.usofa_filter = usofa_filter
        self.region_name = region_name

    def __call__(self):
        reported_accounts = self.get_accounts_from_sqs()
        accounts = self.get_usofa_data()
        usofa_aliases = {aliases for aliases in iter(accounts.keys())}
        # in usofa but not in sqs queue
        usofa_accounts = usofa_aliases.difference(reported_accounts)
        # in sqs but not in usofa
        sqs_accounts = reported_accounts.difference(usofa_aliases)
        if sqs_accounts or usofa_accounts:
            body = self._email_body(usofa_accounts, sqs_accounts)
            self._send_email(self.sender_email, self.recipients, body)

    def get_accounts_from_sqs(self):
        sqs = boto3.resource('sqs', self.region_name)
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
            if not messages:
                break
        return reported_accounts

    def _email_body(self, usofa_accounts, sqs_accounts):
        body = '''Dear AWS User,\n
our Monocyte Alarming identified some suspicious account behaviour during the last 24 hours.'''
        if usofa_accounts:
            body += '''\n\nAccount in AWS account list (Usofa) but monocyte didn't run in this account:'''
            body += '\n\t' + '\n\t'.join(usofa_accounts)
        if sqs_accounts:
            body += '\n\nAccounts not in AWS account list (Usofa) but monocyte ran successfully in this account:\n'
            body += '\n\t' + '\n\t'.join(sqs_accounts)
        body += '\n\nBest,\n\tYour Compliance Team'
        return body

    def _send_email(self, sender_email, recipients, body):
        conn = boto3.client('ses', self.region_name)
        conn.send_email(
            Source=sender_email,
            Message={'Subject': {'Data': 'Monocyte Alarming', 'Charset': 'utf-8'},
                     'Body': {'Text': {'Data': body, 'Charset': 'utf-8'}}},
            Destination={'ToAddresses': recipients})

    def get_usofa_data(self):
        s3_connection = boto3.resource('s3', self.region_name)
        key = s3_connection.Object(self.usofa_bucket, self.usofa_key)
        account_data = json.loads(key.get()['Body'].read().decode('utf-8'))
        filtered_data = {name: data for name, data in account_data.items()
                         if dict_is_subset(self.usofa_filter, data)}
        return filtered_data
