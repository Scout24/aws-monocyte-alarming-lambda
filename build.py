from pybuilder.core import use_plugin, init, Author
import os

use_plugin("python.core")
use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
use_plugin("python.coverage")
use_plugin("python.distutils")
use_plugin("pypi:pybuilder_aws_plugin")

name = "aws-monocyte-alarming-lambda"
version = "0.8"
summary = "aws-monocyte-alarming-lambda - Check SQS messages from monocyte for all ultimiate source of accounts (usofa) and send SES Emails via AWS Lambda"
description = """ 
    Check SQS messages from monocyte for all ultimiate source of accounts and send SES Emails via AWS Lambda.
    """
authors = [Author("Enrico Heine", "enrico.heine@immobilienscout24.de"),
           Author("Michael Kuehne", "michael.kuehne_external@immobilienscout24.de"),
           Author("Thomas Lehmann", "thomas.lehmann@immobilienscout24.de")]
url = "https://github.com/ImmobilienScout24/aws-monocyte-alarming-lambda"
license = "Apache License 2.0"
default_task = ["clean", "analyze", "package_lambda_code"]

@init(environments='upload')
def set_properties_for_teamcity_builds(project):
    project.set_property('teamcity_output', True)
    project.set_property('teamcity_parameter', 'crassus_filename')
    project.set_property('lambda_file_access_control', 'public-read')
    project.set_property('template_file_access_control',
                        os.environ.get('LAMBDA_FILE_ACCESS_CONTROL'))

    # project.version = '%s-%s' % (project.version,
    #                              os.environ.get('BUILD_NUMBER', 0))
    project.default_task = [
        'upload_zip_to_s3',
        'upload_cfn_to_s3',
    ]
    project.set_property('install_dependencies_index_url',
                         os.environ.get('PYPIPROXY_URL'))

    project.set_property('template_files', [
        ('cfn-sphere/templates', 'aws-monocyte-alarming.yaml'),
    ])

@init
def set_properties(project):
    project.set_property("verbose", True)
    project.depends_on("boto3")
    project.depends_on("simplejson")
    project.build_depends_on("moto")
    project.build_depends_on("mock")
    project.build_depends_on("unittest2")
    project.set_property("bucket_name", os.environ.get('BUCKET_NAME_FOR_UPLOAD'))
    project.set_property("lambda_file_access_control", "private")

