import os
import logging
import typing
from time import sleep
import OPi.GPIO as GPIO


FAN_PIN = os.getenv('FAN_PIN', 'PC5')
FAN_ENABLE_THRESHOLD = float(os.getenv('FAN_ENABLE_THRESHOLD', '40'))
FAN_DISABLE_THRESHOLD = float(os.getenv('FAN_DISABLE_THRESHOLD', '30'))
SLEEP_DURATION_SEC = int(os.getenv('SLEEP_DURATION_SEC', '10'))

LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)-15s | %(name)-10s | %(levelname)-8s | %(message)s')
LOG_LEVEL = int(os.getenv('LOG_LEVEL', str(logging.INFO)))

logger = logging.getLogger('FanManager')


class FanManager:
    def __init__(self, pin: str, thresholds: typing.Tuple[float, float]):
        self.pin = pin
        self.threshold_enable, self.threshold_disable = thresholds
        self.enabled = False
        logger.info(f'Variables: FAN_PIN={FAN_PIN}, FAN_ENABLE_THRESHOLD={FAN_ENABLE_THRESHOLD}'
                    f', FAN_DISABLE_THRESHOLD={FAN_DISABLE_THRESHOLD}, SLEEP_DURATION_SEC={SLEEP_DURATION_SEC}'
                    f', LOG_LEVEL={LOG_LEVEL}, LOG_FORMAT="{LOG_FORMAT}"')

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def setup(self):
        logger.debug('Setting up the SUNXI mode')
        GPIO.setmode(GPIO.SUNXI)
        GPIO.setup(self.pin, GPIO.OUT, initial=False)
        GPIO.setwarnings(False)
        logger.info('Setup')

    def cleanup(self):
        self.set_pin(False)
        GPIO.cleanup()
        logger.info('Cleanup')

    def set_pin(self, state: bool):
        GPIO.output(self.pin, state)
        logger.debug(f'Pin #{self.pin} switched to {state}')

    def fan_switch(self, state: bool):
        self.set_pin(state)
        self.enabled = state
        logger.info(f'Fan switched to {state}')

    def fan_control(self):
        cpu_temp = self.get_cpu_temperature()
        if not self.enabled and cpu_temp > self.threshold_enable:
            self.fan_switch(True)
        elif self.enabled and cpu_temp < self.threshold_disable:
            self.fan_switch(False)

    def control_forever(self, sleep_duration_sec: int):
        while True:
            try:
                self.fan_control()
            except KeyboardInterrupt:
                raise
            except Exception as ex:
                logger.exception(ex)
            finally:
                sleep(sleep_duration_sec)

    @staticmethod
    def get_cpu_temperature() -> float:
        with open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r') as fd:
            temp = float(fd.read()) / 1000
            logger.debug(f'CPU temp = {temp}')
            return temp


if __name__ == '__main__':
    logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
    with FanManager(FAN_PIN, (FAN_ENABLE_THRESHOLD, FAN_DISABLE_THRESHOLD)) as fan_manager:
        print(fan_manager)
        fan_manager.control_forever(SLEEP_DURATION_SEC)
