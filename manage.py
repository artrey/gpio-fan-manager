#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import logging
import os
import re

import pytz
import yaml

from fan_manager import FanManager, Schedule, FanPolicy


DEFAULTS = {
    'LOG_FORMAT': '%(asctime)-15s | %(name)-10s | %(levelname)-8s | %(message)s',
    'LOG_LEVEL': logging.INFO,
    'FAN_PIN': 'PC5',
    'SLEEP_DURATION_SEC': 10,
    'TIMEZONE': 'UTC',
    'SCHEDULE': {
        'BASE_POLICY': (40, 30),
        'SPECIAL_POLICIES': [],
    },
}


TIME_PARSER = {part: f'(\d+){part[0]}' for part in ('hour', 'minute', 'second')}


def load_config(path: str) -> dict:
    if path:
        with open(path, 'r') as stream:
            config = yaml.load(stream)
    else:
        config = {}

    for k, v in DEFAULTS.items():
        config.setdefault(k, v)

    return config


def policy_from_dict(data: dict) -> FanPolicy:
    kwargs = {k.lower(): v for k, v in data.items()}

    for param in ['time_start', 'time_finish']:
        time_str = kwargs.get(param, '0h')

        time_args = {}
        for arg, pattern in TIME_PARSER.items():
            match = re.search(pattern, time_str)
            time_args[arg] = int(match.group(1)) if match else 0

        kwargs[param] = datetime.time(**time_args)

    return FanPolicy(**kwargs)


def main():
    config_path = os.getenv('CONFIG_PATH', 'config.yml')
    config = load_config(config_path)

    logging.basicConfig(format=config['LOG_FORMAT'], level=config['LOG_LEVEL'])
    logger = logging.getLogger('Manage')

    logger.debug(f'Initialized logger: LOG_LEVEL={config["LOG_LEVEL"]},'
                 f' LOG_FORMAT="{config["LOG_FORMAT"]}"')

    logger.info(f'Parameters: FAN_PIN={config["FAN_PIN"]},'
                f' SLEEP_DURATION_SEC={config["SLEEP_DURATION_SEC"]},'
                f' TIMEZONE={config["TIMEZONE"]}')

    base_policy = policy_from_dict(config['SCHEDULE']['BASE_POLICY'])
    special_policies = list(map(policy_from_dict, config['SCHEDULE']['SPECIAL_POLICIES']))

    schedule = Schedule(base_policy, special_policies)
    logger.info(f'Actual schedule: {schedule}')

    with FanManager(config['FAN_PIN'], schedule, pytz.timezone(config['TIMEZONE'])) as fan_manager:
        fan_manager.control_forever(config['SLEEP_DURATION_SEC'])


if __name__ == '__main__':
    main()
