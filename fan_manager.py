import os
import logging
import typing
from time import sleep
import OPi.GPIO as GPIO


FAN_PIN = int(os.getenv('FAN_PIN', '18'))
FAN_ENABLE_THRESHOLD = float(os.getenv('FAN_ENABLE_THRESHOLD', '40'))
FAN_DISABLE_THRESHOLD = float(os.getenv('FAN_DISABLE_THRESHOLD', '30'))
SLEEP_DURATION_SEC = int(os.getenv('SLEEP_DURATION_SEC', '10'))

LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)-15s | %(name)-10s | %(levelname)-8s | %(message)s')
LOG_LEVEL = int(os.getenv('LOG_LEVEL', str(logging.INFO)))

logger = logging.getLogger('FanManager')


class FanManager:
    def __init__(self, pin: int, thresholds: typing.Tuple[float, float]):
        self.pin = pin
        self.threshold_enable, self.threshold_disable = thresholds
        self.enabled = False
        logger.info(f'Variables: FAN_PIN={FAN_PIN}, FAN_ENABLE_THRESHOLD={FAN_ENABLE_THRESHOLD}'
                    f', FAN_DISABLE_THRESHOLD={FAN_DISABLE_THRESHOLD}, SLEEP_DURATION_SEC={SLEEP_DURATION_SEC}'
                    f', LOG_LEVEL={LOG_LEVEL}, LOG_FORMAT="{LOG_FORMAT}"')

    @staticmethod
    def setup(pinout: typing.Dict[int, int]):
        GPIO.setmode(GPIO.BCM)
        for pin, mode in pinout.items():
            GPIO.setup(pin, mode)
        GPIO.setwarnings(False)
        logger.info('Setup')

    @staticmethod
    def cleanup():
        GPIO.cleanup()
        logger.info('Cleanup')

    @staticmethod
    def set_pin(pin: int, state: bool):
        GPIO.output(pin, state)
        logger.debug(f'Pin #{pin} switched to {state}')

    @staticmethod
    def get_cpu_temperature() -> float:
        with open('/sys/devices/virtual/thermal/thermal_zone0/temp', 'r') as fd:
            temp = float(fd.read()) / 1000
            logger.debug(f'CPU temp = {temp}')
            return temp

    def fan_switch(self, state: bool):
        self.set_pin(self.pin, state)
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


if __name__ == '__main__':
    try:
        logging.basicConfig(format=LOG_FORMAT, level=LOG_LEVEL)
        FanManager.setup({FAN_PIN: GPIO.OUT})
        FanManager(FAN_PIN, (FAN_ENABLE_THRESHOLD, FAN_DISABLE_THRESHOLD)).control_forever(SLEEP_DURATION_SEC)
    except KeyboardInterrupt:
        FanManager.cleanup()
