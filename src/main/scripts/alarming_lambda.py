from monocyte_alarm import MonocyteAlarm
from aws_lambda_configurer import load_config


def handler(event, context):
    properties = load_config(context)
    sqs_queue = properties['sqs_queue']
    sender_email = properties['sender_email']
    recipients = properties['recipients']
    usofa_key = properties['usofa_key']
    usofa_bucket = properties['usofa_bucket']
    usofa_filter = properties.get('usofa_filter', {})
    region_name = properties['region_name']

    monocyte_alarm = MonocyteAlarm(sqs_queue=sqs_queue,
                                   sender_email=sender_email,
                                   recipients=recipients,
                                   usofa_key=usofa_key,
                                   usofa_bucket=usofa_bucket,
                                   usofa_filter=usofa_filter,
                                   region_name=region_name)
    monocyte_alarm()
