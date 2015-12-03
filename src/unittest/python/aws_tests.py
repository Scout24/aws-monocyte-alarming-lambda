from __future__ import print_function, absolute_import, division
from unittest import TestCase
from mock import patch
import json
from pils_aws import get_lambda_config_property


class PilsTests(TestCase):

    class Context(object):
        def __init__(self):
            self.invoked_function_arn = "42"
            self.function_version = "23"

    class BotoClient(object):
        def __init__(self, return_value):
            self.return_value = return_value

        def get_function_configuration(self, FunctionName=None, Qualifier=None):
            return self.return_value

    def setUp(self):
        self.context = self.Context()

    @patch("boto3.client")
    def test_get_lambda_config_property_with_property(self, mock_boto3_client):
        properties = {
            "key1": 42,
            "key2": "string",
            "key3": [2, 3]
        }
        property_dict = {"Description": json.dumps(properties)}
        mock_boto3_client.return_value = self.BotoClient(property_dict)

        self.assertEqual(get_lambda_config_property(self.context, "key1"), properties['key1'])

    @patch("boto3.client")
    def test_get_lambda_config_property_without_property(self, mock_boto3_client):
        properties = {
            "key1": 42,
            "key2": "string",
            "key3": [2, 3]
        }
        property_dict = {"Description": json.dumps(properties)}
        mock_boto3_client.return_value = self.BotoClient(property_dict)

        self.assertEqual(get_lambda_config_property(self.context), properties)

    @patch("boto3.client")
    def test_get_lambda_config_property_without_json(self, mock_boto3_client):
        property_dict = {"Description": "foobar"}
        mock_boto3_client.return_value = self.BotoClient(property_dict)

        self.assertEqual(get_lambda_config_property(self.context), None)