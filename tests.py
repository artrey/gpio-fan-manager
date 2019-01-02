import unittest
from datetime import time
from manage import policy_from_dict


class TestSchedule(unittest.TestCase):
    def test_policy_from_dict(self):
        self.assertEqual(policy_from_dict({
            'time_start': '20h',
            'time_finish': '6h23m',
            'threshold_enable': 30,
            'threshold_disable': 20
        }).time_finish, time(6, 23))

        self.assertEqual(policy_from_dict({
            'time_start': '20h',
            'time_finish': '15m37s',
            'threshold_enable': 30,
            'threshold_disable': 20
        }).time_finish, time(0, 15, 37))

        self.assertEqual(policy_from_dict({
            'time_start': '20h',
            'time_finish': '6h73m',
            'threshold_enable': 30,
            'threshold_disable': 20
        }).time_finish, time(7, 13))

        self.assertEqual(policy_from_dict({
            'time_start': '20h',
            'time_finish': '24h',
            'threshold_enable': 30,
            'threshold_disable': 20
        }).time_finish, time(0))


if __name__ == '__main__':
    unittest.main()
