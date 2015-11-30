import unittest
import alarming_lambda



class AlarmingLambdaTests(unittest.TestCase):
    def test_handler_call(self):
        alarming_lambda.handler(None, None)
