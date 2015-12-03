from monocyte_alarm import MonocyteAlarm
from pils_aws import get_lambda_config_property


def handler(event, context):
    properties = get_lambda_config_property(context)
    sqs_queue = properties['sqs_queue']
    sender_email = properties['sender_email']
    recipients = properties['recipients']
    dry_run = properties['dry_run']
    usofa_key = properties['usofa_key']
    usofa_bucket = properties['usofa_bucket']
    region_name = properties['region_name']

    monocyte_alarm = MonocyteAlarm(sqs_queue=sqs_queue,
                                   sender_email=sender_email,
                                   recipients=recipients,
                                   usofa_key=usofa_key,
                                   usofa_bucket=usofa_bucket,
                                   region_name=region_name,
                                   dry_run=dry_run
                                   )
    monocyte_alarm()
