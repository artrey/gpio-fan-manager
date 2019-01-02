# -*- coding: utf-8 -*-

import datetime
from typing import List

import pytz


class FanPolicy:
    def __init__(self, time_start: datetime.time, time_finish: datetime.time,
                 threshold_enable: float, threshold_disable: float):
        self.time_start = time_start
        self.time_finish = time_finish
        self.threshold_enable = threshold_enable
        self.threshold_disable = threshold_disable

    def __str__(self):
        return f'[{self.time_start} - {self.time_finish}] {self.threshold_enable} / {self.threshold_disable}'


class Schedule:
    def __init__(self, base_policy: FanPolicy, special_policies: List[FanPolicy]):
        self.base_policy = base_policy
        self.special_policies = special_policies

    def get_policy(self, time: datetime.time) -> FanPolicy:
        def filt(p: FanPolicy):
            if p.time_start > p.time_finish:
                return p.time_start <= time <= datetime.time(23, 59, 59, 999999) \
                       or datetime.time(0) <= time <= p.time_finish
            return p.time_start <= time <= p.time_finish

        return next(filter(filt, self.special_policies), self.base_policy)

    def current_policy(self, tz: pytz.timezone) -> FanPolicy:
        return self.get_policy(datetime.datetime.now(tz=tz).time())

    def __str__(self):
        return f'Base policy: {self.base_policy} | Special policies:' \
               f' {{ {"; ".join(map(str, self.special_policies))} }}'
