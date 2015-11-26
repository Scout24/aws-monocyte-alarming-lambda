from pybuilder.core import use_plugin, init, Author
from pybuilder.vcs import VCSRevision

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")


name = "aws-monocyte-alarming-lambda"
version = '0.1'
summary = 'aws-monocyte-alarming-lambda - Check SQS messages from monocyte for all ultimiate source of accounts (usofa) and send SES Emails via AWS Lambda'
description = """ 
    Check SQS messages from monocyte for all ultimiate source of accounts and send SES Emails via AWS Lambda.
    """
authors = [Author('Enrico Heine', 'enrico.heine@immobilienscout24.de'),
           Author('Michael Kuehne', 'michael.kuehne_external@immobilienscout24.de'),
           Author('Thomas Lehmann', 'thomas.lehmann@immobilienscout24.de')]
url = 'https://github.com/ImmobilienScout24/aws-monocyte-alarming-lambda'
license = 'Apache License 2.0'
default_task = "publish"


@init
def set_properties(project):
    pass
