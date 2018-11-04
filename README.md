# Hardware

You need 4 components:

* Orange Pi PC 2
* 5V fan
* Transistor 2N5551 or analog
* Some wires...

Scheme (see image):

1. Connect 5V pin on board to 5V pin on fan
2. Connect GND pin on board to left pin of transistor
3. Connect GPIO pin on board (e.g. 'PC5' in SUNXI pinout) to middle pin of transistor
4. Connect right pin on transistor to 0V pin on fan

![scheme](scheme.png)

#### SUNXI pinout

![pinout](sunxi-pinout.png)

# Software

### Run script

```bash
pip install requirements.txt
python manage.py
```

Script require access to control of gpio (maybe need sudo).

Script use the config file (default: config.yaml in same folder).
Set the env variable CONFIG_PATH to override file path.

Structure of config file see below.

### Build image

```bash
docker build -t artrey/gpio-fan-manager-arm64 .
```

To use this service in docker need grant it privileged mode. Also need pass the volumes:

* /sys/class/gpio (to control gpio)
* /sys/devices/virtual/thermal/thermal_zone0/temp:ro (to get the temperature)
* /opt/app/config.yml:ro (config file)
* optional: <volume with log file>

Example of docker command:

```bash
docker run -d --restart=always --privileged --name=fan-manager \
    -v /sys/class/gpio:/sys/class/gpio \
    -v /sys/devices/virtual/thermal/thermal_zone0/temp:/sys/devices/virtual/thermal/thermal_zone0/temp:ro \
    -v $PWD/config.yml:/opt/app/config.yml:ro \
    -v $PWD/manager.log:/var/log/manager.log \
    artrey/gpio-fan-manager-arm64
```

Structure of config file see below.

### Structure of config file

Config file is the .yaml/.yml file. Time format is ```<HH>h<MM>m<SS>s```. Hours in 24h-format.

Example of config file:

```yaml
LOG_FILE: ''  # path to log file or empty to log to console
LOG_LEVEL: 20  # python logging level
LOG_FORMAT: '%(asctime)-15s | %(name)-10s | %(levelname)-8s | %(message)s'  # python logging level

FAN_PIN: PC5  # identifier of control pin in SUNXI pinout

SLEEP_DURATION_SEC: 10  # time between check temperature

TIMEZONE: Europe/Moscow  # timezone for correct work schedule

SCHEDULE:  # schedule of manager
  BASE_POLICY:  # policy if not specified policy for current time
    THRESHOLD_ENABLE: 40  # temperature when enable fan
    THRESHOLD_DISABLE: 30  # temperature when disable fan
  SPECIAL_POLICIES:  # list of policies for specify time
    - TIME_START: 22h30m  # night hours
      TIME_FINISH: 2h
      THRESHOLD_ENABLE: 55
      THRESHOLD_DISABLE: 45
    - TIME_START: 2h  # any specific hours
      TIME_FINISH: 13h
      THRESHOLD_ENABLE: 50
      THRESHOLD_DISABLE: 40
```
