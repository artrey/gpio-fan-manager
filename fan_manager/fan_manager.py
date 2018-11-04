# -*- coding: utf-8 -*-

import logging
from time import sleep

import pytz
import OPi.GPIO as GPIO

from fan_manager.schedule import Schedule


class FanManager:
    def __init__(self, pin: str, schedule: Schedule, timezone: pytz.timezone):
        self.pin = pin
        self.schedule = schedule
        self.tz = timezone
        self.enabled = False
        self.logger = logging.getLogger(self.__class__.__name__)

    def __enter__(self):
        # self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def setup(self):
        self.logger.debug('Setting up the SUNXI mode')
        GPIO.setmode(GPIO.SUNXI)
        GPIO.setup(self.pin, GPIO.OUT, initial=False)
        GPIO.setwarnings(False)
        self.logger.info('Setup')

    def cleanup(self):
        self.fan_switch(False)
        GPIO.cleanup()
        self.logger.info('Cleanup')

    def set_pin(self, state: bool):
        GPIO.output(self.pin, state)
        self.logger.debug(f'Pin #{self.pin} switched to {state}')

    def fan_switch(self, state: bool):
        self.set_pin(state)
        self.enabled = state
        self.logger.info(f'Fan switched to {state}')

    def fan_control(self):
        cpu_temp = self.get_cpu_temperature()
        self.logger.debug(f'CPU temp = {cpu_temp}')

        policy = self.schedule.current_policy(self.tz)
        self.logger.debug(f'Active policy: {policy}')

        if not self.enabled and cpu_temp > policy.threshold_enable:
            self.fan_switch(True)
        elif self.enabled and cpu_temp < policy.threshold_disable:
            self.fan_switch(False)

    def control_forever(self, sleep_duration_sec: int):
        while True:
            try:
                self.fan_control()
            except KeyboardInterrupt:
                raise
            except Exception as ex:
                self.logger.exception(ex)
            finally:
                sleep(sleep_duration_sec)

    @staticmethod
    def get_cpu_temperature() -> float:
        with open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r') as fd:
            return float(fd.read()) / 1000
