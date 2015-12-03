from __future__ import print_function, absolute_import, division
import simplejson as json
import boto3


def get_lambda_config_property(context, property_name=None):
    """
    Extract JSON properties from the JSON encoded description.

    Return the value for the property, None if not found,
    all properties if no name given.
    """
    aws_lambda = boto3.client('lambda')
    function_arn = context.invoked_function_arn
    qualifier = context.function_version
    description = aws_lambda.get_function_configuration(
        FunctionName=function_arn,
        Qualifier=qualifier
    )['Description']
    try:
        data = json.loads(description)
        if property_name:
            return_value = data[property_name]
        else:
            return_value = data
        return return_value
    except (ValueError, KeyError):
        return None