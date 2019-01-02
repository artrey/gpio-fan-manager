import unittest
from datetime import time
from .schedule import FanPolicy, Schedule


class TestSchedule(unittest.TestCase):
    def test_base_schedule(self):
        s = Schedule(FanPolicy(time(0), time(0), 40, 30), [])
        self.assertEqual(s.base_policy.threshold_enable, 40)
        self.assertEqual(s.base_policy.threshold_disable, 30)
        self.assertEqual(s.special_policies, [])

    def test_get_policy(self):
        s = Schedule(FanPolicy(time(0), time(0), 40, 30), [
            FanPolicy(time(8), time(12), 40, 20),
            FanPolicy(time(20), time(23, 59, 59, 999999), 30, 10)
        ])

        self.assertEqual(s.get_policy(time(0)).threshold_disable, 30)
        self.assertEqual(s.get_policy(time(1)).threshold_disable, 30)
        self.assertEqual(s.get_policy(time(7, 59, 59)).threshold_disable, 30)

        self.assertEqual(s.get_policy(time(8)).threshold_disable, 20)
        self.assertEqual(s.get_policy(time(12)).threshold_disable, 20)
        self.assertEqual(s.get_policy(time(10, 45)).threshold_disable, 20)

        self.assertEqual(s.get_policy(time(20)).threshold_disable, 10)
        self.assertEqual(s.get_policy(time(22)).threshold_disable, 10)
        self.assertEqual(s.get_policy(time(23, 59, 59)).threshold_disable, 10)


if __name__ == '__main__':
    unittest.main()
