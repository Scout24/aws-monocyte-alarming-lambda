from monocyte_alarm import MonocyteAlarm


def handler(event, context):
    monocyte_alarm = MonocyteAlarm(sqs_queue='monocyte',
                                   sender_email='produktion@immobilienscout24.de',
                                   recipients=['thomas.lehmann@immobilienscout24.de'],
                                   dry_run=True)
    monocyte_alarm()
