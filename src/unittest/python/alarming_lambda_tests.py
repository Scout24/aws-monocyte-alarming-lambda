import unittest2
import boto3
import moto
import json
import monocyte_alarm



class AlarmingLambdaTests(unittest2.TestCase):

    def setUp(self):
        self.usofa_s3_data = '{"my-account": {"id": "123456789012", "email": "test.invalid@test.invalid"}}'
        self.sqs_accounts = [ "my-account", "my-account2" ]
        self.usofa_accounts = [ "usofa-my-account", "usofa-my-account2" ]
        self.sender = "test@test.invalid"
        self.queue_name = 'monocyte'
        self.test_usofa_key = "usofa-key.json"
        self.test_usofa_bucket = "usofa-s3-bucket"
        self.test_region_name = "eu-west-1"
        self.dry_run = "true"
        self.monocyte_alarm = monocyte_alarm.MonocyteAlarm(self.queue_name, self.sender, [self.sender],
                                                           self.test_usofa_key, self.test_usofa_bucket,
                                                           self.test_region_name, self.dry_run)
        self.email_body = '''Dear AWS User,

our Monocyte Alarming identified some suspicious account behaviour during the last 24 hours.

Account in AWS account list (Usofa) but monocyte didn't run in this account:
	usofa-my-account
	usofa-my-account2

Accounts not in AWS account list (Usofa) but monocyte ran successfully in this account:

	my-account
	my-account2

Best,
	Your Compliance Team'''

    @moto.mock_s3
    def test_get_usofa_data(self):
        s3_connection = boto3.client('s3', self.test_region_name)
        s3_connection.create_bucket(Bucket=self.test_usofa_bucket)
        s3_connection.put_object(Bucket=self.test_usofa_bucket, Key=self.test_usofa_key,
                                 Body=self.usofa_s3_data)
        s3_return_value = self.monocyte_alarm.get_usofa_data()
        s3_input_value = json.loads(self.usofa_s3_data)
        self.assertEqual(s3_return_value, s3_input_value)

    def test_email_body(self):
        body = self.monocyte_alarm._email_body(self.usofa_accounts, self.sqs_accounts)
        self.assertEqual(self.email_body, body)

    @moto.mock_ses
    def test_send_email(self):
        conn = boto3.client('ses')
        conn.verify_email_identity(EmailAddress=self.sender)

        self.monocyte_alarm._send_email(self.sender, [self.sender], 'test')

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota['SentLast24Hours'])
        self.assertEqual(sent_count, 1)

    @moto.mock_sqs
    def test_get_accounts_from_sqs(self):
        sqs = boto3.client('sqs')
        qurl = sqs.create_queue(QueueName=self.queue_name)
        for account_name in self.sqs_accounts:
            message_body = '{"status": "no issues", "account": "%s"}' % account_name
            sqs.send_message(QueueUrl=qurl['QueueUrl'],
                             MessageBody=message_body)

        reported_accounts = self.monocyte_alarm.get_accounts_from_sqs()
        self.assertEqual(reported_accounts, set(self.sqs_accounts))

    @moto.mock_sqs
    def test_get_accounts_from_sqs_no_msg(self):
        sqs = boto3.client('sqs')
        sqs.create_queue(QueueName=self.queue_name)

        reported_accounts = self.monocyte_alarm.get_accounts_from_sqs()
        self.assertEqual(reported_accounts, set())

    @moto.mock_sqs
    def test_get_accounts_from_sqs_not_in_usofa(self):
        sqs = boto3.client('sqs')
        qurl = sqs.create_queue(QueueName=self.queue_name)
        for account_name in self.sqs_accounts:
            message_body = '{"status": "no issues", "account": "test_%s"}' % account_name
            sqs.send_message(QueueUrl=qurl['QueueUrl'],
                             MessageBody=message_body)

        reported_accounts = self.monocyte_alarm.get_accounts_from_sqs()
        self.assertEqual(reported_accounts, set(['test_my-account', 'test_my-account2']))

    @moto.mock_sqs
    def test_get_accounts_from_sqs_not_in_sqs_but_in_usofa(self):
        sqs = boto3.client('sqs')
        qurl = sqs.create_queue(QueueName=self.queue_name)
        message_body = '{"status": "no issues", "account": "%s"}' % self.sqs_accounts[0]
        sqs.send_message(QueueUrl=qurl['QueueUrl'], MessageBody=message_body)

        reported_accounts = self.monocyte_alarm.get_accounts_from_sqs()
        self.assertEqual(reported_accounts, set(['my-account']))

    @moto.mock_sqs
    @moto.mock_s3
    @moto.mock_ses
    def test_monocyte_alarm_dry_run(self):
        sqs = boto3.client('sqs')
        qurl = sqs.create_queue(QueueName=self.queue_name)
        for account_name in self.sqs_accounts:
            message_body = '{"status": "no issues", "account": "%s"}' % account_name
            sqs.send_message(QueueUrl=qurl['QueueUrl'],
                             MessageBody=message_body)
        s3_connection = boto3.client('s3', self.test_region_name)
        s3_connection.create_bucket(Bucket=self.test_usofa_bucket)
        s3_connection.put_object(Bucket=self.test_usofa_bucket, Key=self.test_usofa_key,
                                 Body=self.usofa_s3_data)
        conn = boto3.client('ses')
        conn.verify_email_identity(EmailAddress=self.sender)

        self.monocyte_alarm()

        send_quota = conn.get_send_quota()
        sent_count = int(send_quota['SentLast24Hours'])
        self.assertEqual(sent_count, 1)
