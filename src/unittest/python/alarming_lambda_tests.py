import unittest

from monocyte_alarm import monocyte_alarm


class AlarmingLambdaTests(unittest.TestCase):

    def setUp(self):
        pass

    def test_handler_call(self):
        monocyte_alarm()
